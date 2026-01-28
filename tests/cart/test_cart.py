import pytest

from app.middleware.error_handler import DomainError
from app.models import Category, Product
from app.services.cart_service import CartService

def test_cart_add_update_delete(session, users, product_with_inventory):
    user, _ = users
    product, _, _ = product_with_inventory
    added = CartService.add_item(user.id, product.id, 1)
    cart_id = added.id
    item_id = added.items[0].id

    updated = CartService.update_item(user.id, cart_id, item_id, 3)
    assert updated.items[0].quantity == 3

    cleared = CartService.delete_item(user.id, cart_id, item_id)
    assert cleared.items == []

def test_cart_add_fails_when_out_of_stock(session, users):
    user, _ = users
    category = Category(name="Snacks")
    session.add(category)
    session.flush()
    product = Product(name="Chips", sku="SNK1", price="5.00", category_id=category.id)
    session.add(product)
    session.commit()

    with pytest.raises(DomainError) as exc:
        CartService.add_item(user.id, product.id, 1)
    assert exc.value.code == "OUT_OF_STOCK_ANYWHERE"
