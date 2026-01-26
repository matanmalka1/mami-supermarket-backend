"""Tests for address update endpoint."""

from app.models.user import User
from app.models.enums import Role
from app.models.address import Address
from app.extensions import db

class TestUpdateAddress:
    """Tests for PUT /api/v1/me/addresses/:id"""

    def test_update_address_success(self, test_app, auth_header):
        """Should update an existing address."""
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        db.session.add(user)
        db.session.commit()
        address = Address(
            user_id=user.id,
            address_line="123 Main St",
            city="Initial City",
            country="Testland",
            postal_code="12345",
            is_default=False
        )
        db.session.add(address)
        db.session.commit()

        address_id = address.id
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{address_id}",
                json={
                    "city": "Updated City",
                    "postal_code": "00000",
                },
                headers=auth_header(user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["city"] == "Updated City"
            assert data["postal_code"] == "00000"
            # Other fields unchanged
            assert data["address_line"] == address.address_line

    def test_update_address_not_found(self, test_app, auth_header):
        """Should return 404 if address doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        db.session.add(user)
        db.session.commit()
        address = Address(
            user_id=user.id,
            address_line="123 Main St",
            city="Initial City",
            country="Testland",
            postal_code="12345",
            is_default=False
        )
        db.session.add(address)
        db.session.commit()
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{fake_id}",
                json={"city": "New City"},
                headers=auth_header(user),
            )
            assert response.status_code == 404

    def test_update_other_user_address(self, test_app, auth_header):
        """Should return 404 when trying to update another user's address."""
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        db.session.add(user)
        db.session.commit()
        address = Address(
            user_id=user.id,
            address_line="123 Main St",
            city="Initial City",
            country="Testland",
            postal_code="12345",
            is_default=False
        )
        db.session.add(address)
        db.session.commit()
        # Create another user
        other_user = User(
            email="other@example.com",
            full_name="Other User",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        db.session.add(other_user)
        db.session.commit()
        address_id = address.id
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{address_id}",
                json={"city": "Hacked"},
                headers=auth_header(other_user),
            )
            assert response.status_code == 404

    def test_update_address_no_changes(self, test_app, auth_header):
        """Should return unchanged address if no fields provided."""
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        db.session.add(user)
        db.session.commit()
        address = Address(
            user_id=user.id,
            address_line="123 Main St",
            city="Initial City",
            country="Testland",
            postal_code="12345",
            is_default=False
        )
        db.session.add(address)
        db.session.commit()
        address_id = address.id
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{address_id}",
                json={},
                headers=auth_header(user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["city"] == address.city
