from __future__ import annotations
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
        category_id: int,
        branch_id: int | None,
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
    def get_product(product_id: int, branch_id: int | None) -> ProductResponse:
        stmt = sa.select(Product).where(Product.id == product_id).options(selectinload(Product.inventory).selectinload(Inventory.branch))
        product = db.session.execute(stmt).scalar_one_or_none()
        if not product or not product.is_active:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        return to_product_response(product, branch_id)

    @staticmethod
    def search_products(
        query: str | None,
        category_id: int | None,
        in_stock: bool | None,
        branch_id: int | None,
        limit: int,
        offset: int,
        min_price: float | None = None,
        max_price: float | None = None,
        organic_only: bool | None = None,
        sort: str | None = None,
    ) -> tuple[list[ProductResponse], int]:
        base = sa.select(Product).where(Product.is_active.is_(True))
        if query:
            base = base.where(Product.name.ilike(f"%{query}%"))
        if category_id:
            base = base.where(Product.category_id == category_id)
        if min_price is not None:
            base = base.where(Product.price >= min_price)
        if max_price is not None:
            base = base.where(Product.price <= max_price)
        if organic_only:
            base = base.where(Product.is_organic.is_(True))
        # Sorting
        if sort == "price_asc":
            base = base.order_by(Product.price.asc())
        elif sort == "price_desc":
            base = base.order_by(Product.price.desc())
        elif sort == "updated_at_desc":
            base = base.order_by(Product.updated_at.desc())
        elif sort == "name_asc":
            base = base.order_by(Product.name.asc())
        elif sort == "name_desc":
            base = base.order_by(Product.name.desc())
        else:
            base = base.order_by(Product.id.desc())
        stmt = base.options(selectinload(Product.inventory).selectinload(Inventory.branch)).offset(offset).limit(limit)
        products = db.session.execute(stmt).scalars().all()
        if in_stock is not None:
            products = [p for p in products if matches_stock(p, branch_id, in_stock)]
            total = len(products)
        else:
            # Count total (ignoring offset/limit)
            count_base = sa.select(sa.func.count()).select_from(Product).where(Product.is_active.is_(True))
            if query:
                count_base = count_base.where(Product.name.ilike(f"%{query}%"))
            if category_id:
                count_base = count_base.where(Product.category_id == category_id)
            if min_price is not None:
                count_base = count_base.where(Product.price >= min_price)
            if max_price is not None:
                count_base = count_base.where(Product.price <= max_price)
            if organic_only:
                count_base = count_base.where(Product.is_organic.is_(True))
            total = db.session.scalar(count_base)
        return map_products(products, branch_id), total or 0

    @staticmethod
    def featured_products(limit: int, branch_id: int | None) -> list[ProductResponse]:
        stmt = (
            sa.select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.updated_at.desc(), Product.id.desc())
            .limit(limit)
            .options(selectinload(Product.inventory).selectinload(Inventory.branch))
        )
        products = db.session.execute(stmt).scalars().all()
        return map_products(products, branch_id)

    @staticmethod
    def autocomplete(query: str | None, limit: int) -> AutocompleteResponse:
        stmt = sa.select(Product).where(Product.is_active.is_(True))
        if query:
            stmt = stmt.where(Product.name.ilike(f"%{query}%"))
        products = db.session.execute(stmt.limit(limit)).scalars().all()
        items = [AutocompleteItem(id=p.id, name=p.name) for p in products]
        return AutocompleteResponse(total=len(items), limit=limit, offset=0, items=items)
