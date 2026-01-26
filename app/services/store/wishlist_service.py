from __future__ import annotations

from ...extensions import db
from ...middleware.error_handler import DomainError
from ...models import Product, WishlistItem


class WishlistService:
    """Manage a user's wishlist entries."""

    @staticmethod
    def list_items(user_id: int) -> list[dict]:
        items = (
            db.session.query(WishlistItem)
            .filter_by(user_id=user_id)
            .order_by(WishlistItem.created_at.desc())
            .all()
        )
        return [
            {
                "product_id": str(item.product_id),
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ]

    @staticmethod
    def add_item(user_id: int, product_id: int) -> dict:
        product = db.session.get(Product, product_id)
        if not product:
            raise DomainError("PRODUCT_NOT_FOUND", "Product not found", status_code=404)
        existing = (
            db.session.query(WishlistItem)
            .filter_by(user_id=user_id, product_id=product_id)
            .first()
        )
        if existing:
            return {
                "product_id": str(existing.product_id),
                "created_at": existing.created_at.isoformat(),
            }
        item = WishlistItem(user_id=user_id, product_id=product_id)
        db.session.add(item)
        db.session.commit()
        return {
            "product_id": str(item.product_id),
            "created_at": item.created_at.isoformat(),
        }

    @staticmethod
    def remove_item(user_id: int, product_id: int) -> bool:
        item = (
            db.session.query(WishlistItem)
            .filter_by(user_id=user_id, product_id=product_id)
            .first()
        )
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True
