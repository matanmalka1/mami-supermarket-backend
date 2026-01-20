from __future__ import annotations
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Category, Inventory, Product
from app.schemas.catalog import AutocompleteItem, AutocompleteResponse, CategoryResponse, ProductResponse
from .mappers import map_products, matches_stock, to_category_response, to_product_response


class CatalogQueryService:
    @staticmethod
    def list_categories(limit: int, offset: int) -> tuple[list[CategoryResponse], int]:
        stmt = sa.select(Category).where(Category.is_active.is_(True)).offset(offset).limit(limit)
        categories = db.session.execute(stmt).scalars().all()
        total = db.session.scalar(sa.select(sa.func.count()).select_from(Category).where(Category.is_active.is_(True)))
        return ([to_category_response(c) for c in categories], total or 0)

    @staticmethod
    def get_category_products(
        category_id: UUID,
        branch_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[list[ProductResponse], int]:
        stmt = (
            sa.select(Product)
            .where(Product.category_id == category_id)
            .where(Product.is_active.is_(True))
            .options(selectinload(Product.inventory).selectinload(Inventory.branch))
            .offset(offset)
            .limit(limit)
        )
        products = db.session.execute(stmt).scalars().all()
        total = db.session.scalar(
            sa.select(sa.func.count())
            .select_from(Product)
            .where(Product.category_id == category_id)
            .where(Product.is_active.is_(True))
        )
        return map_products(products, branch_id), total or 0

    @staticmethod
    def get_product(product_id: UUID, branch_id: UUID | None) -> ProductResponse:
        stmt = sa.select(Product).where(Product.id == product_id).options(selectinload(Product.inventory).selectinload(Inventory.branch))
        product = db.session.execute(stmt).scalar_one_or_none()
        if not product or not product.is_active:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        return to_product_response(product, branch_id)

    @staticmethod
    def search_products(
        query: str | None,
        category_id: UUID | None,
        in_stock: bool | None,
        branch_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[list[ProductResponse], int]:
        base = sa.select(Product).where(Product.is_active.is_(True))
        if query:
            base = base.where(Product.name.ilike(f"%{query}%"))
        if category_id:
            base = base.where(Product.category_id == category_id)
        stmt = base.options(selectinload(Product.inventory).selectinload(Inventory.branch)).offset(offset).limit(limit)
        products = db.session.execute(stmt).scalars().all()
        if in_stock is not None:
            products = [p for p in products if matches_stock(p, branch_id, in_stock)]
        count_stmt = sa.select(sa.func.count()).select_from(base.subquery())
        total = len(products) if in_stock is not None else db.session.scalar(count_stmt)
        return map_products(products, branch_id), total or 0

    @staticmethod
    def autocomplete(query: str | None, limit: int) -> AutocompleteResponse:
        stmt = sa.select(Product).where(Product.is_active.is_(True))
        if query:
            stmt = stmt.where(Product.name.ilike(f"%{query}%"))
        products = db.session.execute(stmt.limit(limit)).scalars().all()
        items = [AutocompleteItem(id=p.id, name=p.name) for p in products]
        return AutocompleteResponse(total=len(items), limit=limit, offset=0, items=items)
