from __future__ import annotations

from ..extensions import db
from ..middleware.error_handler import DomainError
from ..models import Cart, CartItem
from ..schemas.cart import CartResponse
from ..services.audit_service import AuditService
from .cart import helpers, validators


class CartService:
    @staticmethod
    def _audit(cart_id: int, action: str, actor_user_id: int | None, **kwargs) -> None:
        AuditService.log_event(
            entity_type="cart",
            action=action,
            entity_id=cart_id,
            actor_user_id=actor_user_id,
            **kwargs,
        )
    
    @staticmethod
    def get_cart(user_id: int) -> CartResponse:
        """Get user's cart."""
        cart = helpers.get_or_create_cart(user_id)
        return helpers.to_response(cart)

    @staticmethod
    def add_item(user_id: int, product_id: int, quantity: int) -> CartResponse:
        """Add item to cart."""
        if quantity <= 0:
            raise DomainError("INVALID_QUANTITY", "Quantity must be positive")
        
        product = validators.validate_product(product_id)
        validators.assert_in_stock_anywhere(product)
        
        cart = helpers.get_or_create_cart(user_id)
        existing = next((i for i in cart.items if i.product_id == product_id), None)
        requested_quantity = quantity + existing.quantity if existing else quantity
        validators.assert_in_stock_delivery_branch(product, requested_quantity)
        
        if existing:
            existing.quantity += quantity
            existing.unit_price = product.price
            db.session.add(existing)
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price,
            )
            db.session.add(item)
        db.session.commit()

        CartService._audit(
            cart.id, "ADD_ITEM", user_id,
            new_value={"product_id": str(product_id), "quantity": quantity}
        )
        return helpers.to_response(helpers.reload_cart(cart.id))

    @staticmethod
    def update_item(user_id: int, cart_id: int, item_id: int, quantity: int) -> CartResponse:
        """Update cart item quantity."""
        if quantity <= 0:
            raise DomainError("INVALID_QUANTITY", "Quantity must be positive")
        
        cart = CartService._get_cart_for_user(cart_id, user_id)
        item = db.session.get(CartItem, item_id)

        if not item or item.cart_id != cart.id:
            raise DomainError("NOT_FOUND", "Cart item not found", status_code=404)
        
        product = validators.validate_product(item.product_id)
        validators.assert_in_stock_anywhere(product)
        validators.assert_in_stock_delivery_branch(product, quantity)

        old_qty = item.quantity
        item.quantity = quantity
        db.session.add(item)
        db.session.commit()

        CartService._audit(
            cart.id, "UPDATE_ITEM", user_id,
            old_value={"item_id": str(item_id), "quantity": old_qty},
            new_value={"item_id": str(item_id), "quantity": quantity},
        )
        return helpers.to_response(helpers.reload_cart(cart.id))
    
    @staticmethod
    def delete_item(user_id: int, cart_id: int, item_id: int) -> CartResponse:
        """Delete cart item."""
        cart = CartService._get_cart_for_user(cart_id, user_id)
        item = db.session.get(CartItem, item_id)
        if not item or item.cart_id != cart.id:
            raise DomainError("NOT_FOUND", "Cart item not found", status_code=404)
        db.session.delete(item)
        db.session.commit()
        CartService._audit(cart.id, "DELETE_ITEM", user_id, old_value={"item_id": str(item_id)})
        return helpers.to_response(helpers.reload_cart(cart.id))
    
    @staticmethod
    def clear_cart(user_id: int, cart_id: int) -> CartResponse:
        """Clear all items from cart."""
        cart = CartService._get_cart_for_user(cart_id, user_id)
        for item in list(cart.items):
            db.session.delete(item)
        db.session.commit()
        CartService._audit(cart.id, "CLEAR", user_id)
        return helpers.to_response(helpers.reload_cart(cart.id))
    
    @staticmethod
    def _get_cart_for_user(cart_id: int, user_id: int) -> Cart:
        """Get cart and verify ownership."""
        cart = db.session.get(Cart, cart_id)
        if not cart or cart.user_id != user_id:
            raise DomainError("NOT_FOUND", "Cart not found", status_code=404)
        return cart
