"""Tests for address list and create endpoints."""

class TestListAddresses:
    """Tests for GET /api/v1/me/addresses"""

    def test_list_addresses_empty(self, test_app, customer_user, auth_header):
        """Should return empty list if user has no addresses."""
        with test_app.test_client() as client:
            response = client.get("/api/v1/me/addresses", headers=auth_header(customer_user))
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert isinstance(data, list) and len(data) == 0

    def test_list_addresses_with_data(self, test_app, customer_with_addresses, auth_header):
        """Should return user's addresses sorted by default first."""
        user, addresses = customer_with_addresses
        with test_app.test_client() as client:
            response = client.get("/api/v1/me/addresses", headers=auth_header(user))
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert len(data) == 2
            assert data[0]["is_default"] is True
            assert data[0]["address_line"] == "123 Main St"
            assert data[1]["is_default"] is False

    def test_list_addresses_unauthorized(self, test_app):
        """Should fail without authentication."""
        with test_app.test_client() as client:
            response = client.get("/api/v1/me/addresses")
            assert response.status_code == 401

class TestCreateAddress:
    """Tests for POST /api/v1/me/addresses"""

    def test_create_address_success(self, test_app, customer_user, auth_header):
        """Should create a new address."""
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/me/addresses",
                json={
                    "address_line": "789 New St",
                    "city": "Haifa",
                    "postal_code": "11111",
                    "country": "Israel",
                    "is_default": False,
                },
                headers=auth_header(customer_user),
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["address_line"] == "789 New St"
            assert data["city"] == "Haifa"
            assert data["is_default"] is False
            assert data["user_id"] == customer_user.id

    def test_create_default_address(self, test_app, customer_with_addresses, auth_header):
        """Should create default address and unset previous default."""
        user, old_addresses = customer_with_addresses
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/me/addresses",
                json={
                    "address_line": "New Default St",
                    "city": "Eilat",
                    "postal_code": "99999",
                    "country": "Israel",
                    "is_default": True,
                },
                headers=auth_header(user),
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["is_default"] is True

            # Verify only one default exists
            list_response = client.get("/api/v1/me/addresses", headers=auth_header(user))
            addresses = list_response.get_json()["data"]
            defaults = [a for a in addresses if a["is_default"]]
            assert len(defaults) == 1
            assert defaults[0]["address_line"] == "New Default St"

    def test_create_address_missing_fields(self, test_app, customer_user, auth_header):
        """Should fail if required fields are missing."""
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/me/addresses",
                json={"address_line": "Incomplete"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 400
