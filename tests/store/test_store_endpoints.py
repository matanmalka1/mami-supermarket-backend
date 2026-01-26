"""Storefront endpoint smoke tests."""

from app.models import Product

def test_store_notifications_empty(client, customer_user, auth_header):
    response = client.get(
        "/api/v1/store/notifications", headers=auth_header(customer_user)
    )
    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["items"] == []
    assert payload["unread_count"] == 0


def test_store_shipping_info_contains_policies(client):
    response = client.get("/api/v1/store/shipping-info")
    assert response.status_code == 200
    policies = response.get_json()["data"]["policies"]
    assert isinstance(policies, list) and len(policies) > 0


def test_store_wishlist_requires_auth(client):
    response = client.get("/api/v1/store/wishlist")
    assert response.status_code == 401


def test_store_wishlist_add_list_remove(client, session, customer_user, auth_header):
    product = session.query(Product).first()
    headers = auth_header(customer_user)
    add_resp = client.post(
        "/api/v1/store/wishlist", json={"product_id": str(product.id)}, headers=headers
    )
    assert add_resp.status_code == 200
    assert add_resp.get_json()["data"]["product_id"] == str(product.id)

    list_resp = client.get("/api/v1/store/wishlist", headers=headers)
    items = list_resp.get_json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["product_id"] == str(product.id)

    remove_resp = client.delete(
        f"/api/v1/store/wishlist/{product.id}", headers=headers
    )
    assert remove_resp.status_code == 200
    assert remove_resp.get_json()["data"]["removed"] is True

    list_empty = client.get("/api/v1/store/wishlist", headers=headers)
    assert list_empty.get_json()["data"]["items"] == []
