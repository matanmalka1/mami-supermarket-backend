from __future__ import annotations
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Category, Product
from app.schemas.catalog import CategoryResponse, ProductResponse
from app.services.audit_service import AuditService
from .mappers import to_category_response, to_product_response


class CatalogAdminService:
    @staticmethod
    def create_category(name: str, description: str | None) -> CategoryResponse:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        AuditService.log_event(entity_type="category", action="CREATE", entity_id=category.id)
        return to_category_response(category)

    @staticmethod
    def update_category(category_id: UUID, name: str, description: str | None) -> CategoryResponse:
        category = db.session.get(Category, category_id)
        if not category:
            raise DomainError("NOT_FOUND", "Category not found", status_code=404)
        old_value = {"name": category.name, "description": category.description}
        category.name = name
        category.description = description
        db.session.add(category)
        db.session.commit()
        AuditService.log_event(
            entity_type="category",
            action="UPDATE",
            entity_id=category.id,
            old_value=old_value,
            new_value={"name": name, "description": description},
        )
        return to_category_response(category)

    @staticmethod
    def toggle_category(category_id: UUID, active: bool) -> CategoryResponse:
        category = db.session.get(Category, category_id)
        if not category:
            raise DomainError("NOT_FOUND", "Category not found", status_code=404)
        category.is_active = active
        db.session.add(category)
        db.session.commit()
        AuditService.log_event(
            entity_type="category",
            action="DEACTIVATE" if not active else "ACTIVATE",
            entity_id=category.id,
            new_value={"is_active": active},
        )
        return to_category_response(category)

    @staticmethod
    def create_product(
        name: str,
        sku: str,
        price: str,
        category_id: UUID,
        description: str | None,
    ) -> ProductResponse:
        category = db.session.get(Category, category_id)
        if not category:
            raise DomainError("NOT_FOUND", "Category not found", status_code=404)
        product = Product(
            name=name,
            sku=sku,
            price=price,
            description=description,
            category_id=category_id,
        )
        try:
            db.session.add(product)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError(
                "DATABASE_ERROR",
                "Could not create product",
                details={"error": str(exc)},
            ) from exc
        AuditService.log_event(entity_type="product", action="CREATE", entity_id=product.id)
        return to_product_response(product, None)

    @staticmethod
    def update_product(
        product_id: UUID,
        name: str | None,
        sku: str | None,
        price: str | None,
        category_id: UUID | None,
        description: str | None,
    ) -> ProductResponse:
        product = db.session.get(Product, product_id)
        if not product:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        old_value = {
            "name": product.name,
            "sku": product.sku,
            "price": str(product.price),
            "category_id": str(product.category_id),
            "description": product.description,
        }
        if name:
            product.name = name
        if sku:
            product.sku = sku
        if price:
            product.price = price
        if category_id:
            product.category_id = category_id
        if description is not None:
            product.description = description
        db.session.add(product)
        db.session.commit()
        AuditService.log_event(
            entity_type="product",
            action="UPDATE",
            entity_id=product.id,
            old_value=old_value,
            new_value={
                "name": product.name,
                "sku": product.sku,
                "price": str(product.price),
                "category_id": str(product.category_id),
                "description": product.description,
            },
        )
        return to_product_response(product, None)

    @staticmethod
    def toggle_product(product_id: UUID, active: bool) -> ProductResponse:
        product = db.session.get(Product, product_id)
        if not product:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        product.is_active = active
        db.session.add(product)
        db.session.commit()
        AuditService.log_event(
            entity_type="product",
            action="DEACTIVATE" if not active else "ACTIVATE",
            entity_id=product.id,
            new_value={"is_active": active},
        )
        return to_product_response(product, None)
