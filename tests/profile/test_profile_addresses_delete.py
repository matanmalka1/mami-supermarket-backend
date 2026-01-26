"""Tests for address delete endpoint."""

from app.models import User, Address
from app.models.enums import Role

class TestDeleteAddress:
    """Tests for DELETE /api/v1/me/addresses/:id"""

    def test_delete_address_success(self, test_app, customer_with_addresses, auth_header, session):
        """Should delete an address."""
        user, addresses = customer_with_addresses
        with test_app.test_client() as client:
            response = client.delete(
                f"/api/v1/me/addresses/{addresses[1].id}", headers=auth_header(user)
            )
            assert response.status_code == 200
            assert "message" in response.get_json()["data"]
            assert len(session.query(Address).filter_by(user_id=user.id).all()) == 1

    def test_delete_address_not_found(self, test_app, customer_user, auth_header):
        """Should return 404 if address doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        with test_app.test_client() as client:
            response = client.delete(f"/api/v1/me/addresses/{fake_id}", headers=auth_header(customer_user))
            assert response.status_code == 404

    def test_delete_other_user_address(self, test_app, customer_with_addresses, session, auth_header):
        """Should return 404 when trying to delete another user's address."""
        user, addresses = customer_with_addresses
        other_user = User(email="other2@example.com", full_name="Other User 2", password_hash="hash", role=Role.CUSTOMER)
        session.add(other_user)
        session.commit()
        with test_app.test_client() as client:
            response = client.delete(f"/api/v1/me/addresses/{addresses[0].id}", headers=auth_header(other_user))
            assert response.status_code == 404
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
            assert data["id"] == str(non_default_id)

            # Verify only one default exists
            list_response = client.get(
                "/api/v1/me/addresses",
                headers=auth_header(user),
            )
            all_addresses = list_response.get_json()["data"]
            defaults = [a for a in all_addresses if a["is_default"]]
            assert len(defaults) == 1
            assert defaults[0]["id"] == str(non_default_id)

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
