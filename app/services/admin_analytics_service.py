from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy import table, column, DateTime, Numeric, Enum, func, cast, select
from app.extensions import db
from app.models.enums import OrderStatus

class AdminAnalyticsService:
    @staticmethod
    def get_revenue(range_: str = "30d", granularity: str = None):
        now = datetime.utcnow()
        if range_ == "12m":
            start = now.replace(day=1, month=now.month, year=now.year) - timedelta(days=365)
            gran = "month"
        elif range_ == "90d":
            start = now - timedelta(days=90)
            gran = "day"
        else:
            start = now - timedelta(days=30)
            gran = "day"
        if granularity:
            gran = granularity

        RevenueTable = table(
            "orders",
            column("created_at", DateTime),
            column("total_amount", Numeric(12, 2)),
            column("status", Enum(OrderStatus, name="order_status")),
        )

        is_sqlite = hasattr(db, 'engine') and db.engine and db.engine.dialect.name == "sqlite"
        created_at = RevenueTable.c.created_at
        if is_sqlite:
            label_expr = (
                func.strftime('%Y-%m', created_at)
                if gran == "month"
                else func.strftime('%Y-%m-%d', created_at)
            )
        else:
            if gran == "month":
                label_expr = func.to_char(
                    func.date_trunc('month', created_at),
                    'YYYY-MM',
                )
            else:
                label_expr = func.to_char(
                    func.date_trunc('day', created_at),
                    'YYYY-MM-DD',
                )

        status_filter = RevenueTable.c.status == OrderStatus.DELIVERED
        q = (
            select(
                label_expr.label("label"),
                func.coalesce(
                    func.sum(cast(RevenueTable.c.total_amount, sa.Numeric(12, 2))),
                    0,
                ).label("value"),
            )
            .select_from(RevenueTable)
            .where(
                sa.and_(
                    status_filter,
                    RevenueTable.c.created_at >= sa.bindparam("start"),
                ),
            )
            .group_by(label_expr)
            .order_by(label_expr)
        )
        result = db.session.execute(q, {"start": start}).fetchall()
        labels = [row.label for row in result]
        values = [float(row.value) for row in result]
        return {"labels": labels, "values": values}
