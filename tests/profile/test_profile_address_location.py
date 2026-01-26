"""Tests for address location tagging."""

from app.models.enums import Role

def test_update_address_location_success(
    client,
    session,
    customer_with_addresses,
    auth_header,
):
    user, addresses = customer_with_addresses
    address = addresses[0]
    payload = {"lat": 32.123, "lng": 34.987}
    response = client.patch(
        f"/api/v1/me/addresses/{address.id}/location",
        json=payload,
        headers=auth_header(user),
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["lat"] == payload["lat"]
    assert data["lng"] == payload["lng"]
    session.refresh(address)
    assert address.latitude == payload["lat"]
    assert address.longitude == payload["lng"]


def test_update_address_location_owner_only(
    client,
    session,
    customer_with_addresses,
    auth_header,
    create_user_with_role,
):
    user, addresses = customer_with_addresses
    attacker = create_user_with_role(Role.CUSTOMER)
    response = client.patch(
        f"/api/v1/me/addresses/{addresses[0].id}/location",
        json={"lat": 0.0, "lng": 0.0},
        headers=auth_header(attacker),
    )
    assert response.status_code == 404


def test_update_address_location_invalid_payload(client, customer_with_addresses, auth_header):
    user, address_list = customer_with_addresses
    response = client.patch(
        f"/api/v1/me/addresses/{address_list[0].id}/location",
        json={"lat": "nope"},
        headers=auth_header(user),
    )
    assert response.status_code == 400
