from __future__ import annotations
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..extensions import db
from ..middleware.error_handler import DomainError
from ..models import Cart, CartItem, Inventory, Product
from ..schemas.cart import CartItemResponse, CartResponse
from ..services.audit_service import AuditService


class CartService:
    @staticmethod
    def _audit(cart_id: UUID, action: str, actor_user_id: UUID | None, **kwargs) -> None:
        AuditService.log_event(
            entity_type="cart",
            action=action,
            entity_id=cart_id,
            actor_user_id=actor_user_id,
            **kwargs,
        )
    @staticmethod
    def get_or_create_cart(user_id: UUID) -> Cart:
        cart = db.session.query(Cart).options(selectinload(Cart.items)).filter_by(user_id=user_id).first()
        if cart is None:
            cart = Cart(id=uuid4(), user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        return cart
    
    @staticmethod
    def get_cart(user_id: UUID) -> CartResponse:
        return CartService._to_response(CartService.get_or_create_cart(user_id))

    @staticmethod
    def add_item(user_id: UUID, product_id: UUID, quantity: int) -> CartResponse:
        if quantity <= 0:
            raise DomainError("INVALID_QUANTITY", "Quantity must be positive")
        
        product = CartService._validate_product(product_id)
        CartService._assert_in_stock_anywhere(product)
        cart = CartService.get_or_create_cart(user_id)
        existing = next((i for i in cart.items if i.product_id == product_id), None)
        if existing:
            existing.quantity += quantity
            existing.unit_price = product.price
            db.session.add(existing)
        else:
            item = CartItem(
                id=uuid4(),
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price,
            )
            db.session.add(item)
        db.session.commit()

        CartService._audit(cart.id, "ADD_ITEM", user_id, new_value={"product_id": str(product_id), "quantity": quantity})
        return CartService._to_response(CartService._reload_cart(cart.id))
    
    @staticmethod
    def update_item(user_id: UUID, cart_id: UUID, item_id: UUID, quantity: int) -> CartResponse:
        if quantity <= 0:
            raise DomainError("INVALID_QUANTITY", "Quantity must be positive")
        
        cart = CartService._get_cart_for_user(cart_id, user_id)
        item = db.session.get(CartItem, item_id)

        if not item or item.cart_id != cart.id:
            raise DomainError("NOT_FOUND", "Cart item not found", status_code=404)
        
        product = CartService._validate_product(item.product_id)
        CartService._assert_in_stock_anywhere(product)

        old_qty = item.quantity
        item.quantity = quantity
        db.session.add(item)
        db.session.commit()

        CartService._audit(
            cart.id,
            "UPDATE_ITEM",
            user_id,
            old_value={"item_id": str(item_id), "quantity": old_qty},
            new_value={"item_id": str(item_id), "quantity": quantity},
        )
        return CartService._to_response(CartService._reload_cart(cart.id))
    
    @staticmethod
    def delete_item(user_id: UUID, cart_id: UUID, item_id: UUID) -> CartResponse:
        cart = CartService._get_cart_for_user(cart_id, user_id)
        item = db.session.get(CartItem, item_id)
        if not item or item.cart_id != cart.id:
            raise DomainError("NOT_FOUND", "Cart item not found", status_code=404)
        db.session.delete(item)
        db.session.commit()
        CartService._audit(cart.id, "DELETE_ITEM", user_id, old_value={"item_id": str(item_id)})
        return CartService._to_response(CartService._reload_cart(cart.id))
    
    @staticmethod
    def clear_cart(user_id: UUID, cart_id: UUID) -> CartResponse:
        cart = CartService._get_cart_for_user(cart_id, user_id)
        for item in list(cart.items):
            db.session.delete(item)
        db.session.commit()
        CartService._audit(cart.id, "CLEAR", user_id)
        return CartService._to_response(CartService._reload_cart(cart.id))
    
    @staticmethod
    def _validate_product(product_id: UUID) -> Product:
        product = db.session.get(Product, product_id)
        if not product or not product.is_active:
            raise DomainError("PRODUCT_INACTIVE", "Product is inactive or missing", status_code=404)
        return product
    
    @staticmethod
    def _assert_in_stock_anywhere(product: Product) -> None:
        total_available = db.session.scalar(select(func.coalesce(func.sum(Inventory.available_quantity), 0)).where(Inventory.product_id == product.id))
        if total_available is None or total_available <= 0:
            raise DomainError("OUT_OF_STOCK_ANYWHERE", "Product is out of stock")
        
    @staticmethod
    def _get_cart_for_user(cart_id: UUID, user_id: UUID) -> Cart:
        cart = db.session.get(Cart, cart_id)
        if not cart or cart.user_id != user_id:
            raise DomainError("NOT_FOUND", "Cart not found", status_code=404)
        return cart
    
    @staticmethod
    def _reload_cart(cart_id: UUID) -> Cart:
        return db.session.execute(select(Cart).where(Cart.id == cart_id).options(selectinload(Cart.items))).scalar_one()

    @staticmethod
    def _to_response(cart: Cart) -> CartResponse:
        items = [
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=Decimal(item.unit_price),
            )
            for item in cart.items
        ]
        total = sum(item.unit_price * item.quantity for item in items)
        return CartResponse(id=cart.id, user_id=cart.user_id, total_amount=total, items=items)
