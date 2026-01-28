"""Tests for set default address endpoint."""

from app.models import User
from app.models.enums import Role

class TestSetDefaultAddress:
    """Tests for PATCH /api/v1/me/addresses/:id/default"""

    def test_set_default_address_success(self, test_app, customer_with_addresses, auth_header):
        """Should set an address as default and unset others."""
        user, addresses = customer_with_addresses
        non_default_id = addresses[1].id
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/me/addresses/{non_default_id}/default",
                headers=auth_header(user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_default"] is True
            assert data["id"] == non_default_id

            # Verify only one default exists
            list_response = client.get(
                "/api/v1/me/addresses",
                headers=auth_header(user),
            )
            all_addresses = list_response.get_json()["data"]
            defaults = [a for a in all_addresses if a["is_default"]]
            assert len(defaults) == 1
            assert defaults[0]["id"] == non_default_id

    def test_set_default_address_not_found(self, test_app, customer_user, auth_header):
        """Should return 404 if address doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/me/addresses/{fake_id}/default",
                headers=auth_header(customer_user),
            )
            assert response.status_code == 404

    def test_set_default_other_user_address(self, test_app, customer_with_addresses, session, auth_header):
        """Should return 404 when trying to set another user's address as default."""
        user, addresses = customer_with_addresses
        other_user = User(
            email="other3@example.com",
            full_name="Other User 3",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        session.add(other_user)
        session.commit()

        address_id = addresses[0].id
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/me/addresses/{address_id}/default",
                headers=auth_header(other_user),
            )
            assert response.status_code == 404

    def test_set_already_default_address(self, test_app, customer_with_addresses, auth_header):
        """Should work even if address is already default."""
        user, addresses = customer_with_addresses
        default_id = addresses[0].id  # Already default
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/me/addresses/{default_id}/default",
                headers=auth_header(user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_default"] is True
