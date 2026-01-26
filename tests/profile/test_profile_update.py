"""Tests for user profile update endpoints."""

class TestUpdatePhone:
    """Tests for PATCH /api/v1/me/phone"""

    def test_update_phone_success(self, test_app, customer_user, auth_header):
        """Should update user's phone number."""
        with test_app.test_client() as client:
            response = client.patch(
                "/api/v1/me/phone",
                json={"phone": "9876543210"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["phone"] == "9876543210"
            assert data["id"] == str(customer_user.id)

    def test_update_phone_missing_field(self, test_app, customer_user, auth_header):
        """Should fail if phone field is missing."""
        with test_app.test_client() as client:
            response = client.patch(
                "/api/v1/me/phone",
                json={},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 400

    def test_update_phone_unauthorized(self, test_app):
        """Should fail without authentication."""
        with test_app.test_client() as client:
            response = client.patch(
                "/api/v1/me/phone",
                json={"phone": "9876543210"},
            )
            assert response.status_code == 401


class TestUpdateProfile:
    """Tests for PATCH /api/v1/me"""

    def test_update_full_name(self, test_app, customer_user, auth_header):
        """Should update user's full name."""
        with test_app.test_client() as client:
            response = client.patch(
                "/api/v1/me",
                json={"full_name": "Updated Name"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["full_name"] == "Updated Name"
            assert data["phone"] == customer_user.phone

    def test_update_phone_via_profile(self, test_app, customer_user, auth_header):
        """Should update phone via profile endpoint."""
        with test_app.test_client() as client:
            response = client.patch(
                "/api/v1/me",
                json={"phone": "1111111111"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["phone"] == "1111111111"

    def test_update_both_fields(self, test_app, customer_user, auth_header):
        """Should update both full_name and phone."""
        with test_app.test_client() as client:
            response = client.patch(
                "/api/v1/me",
                json={"full_name": "New Name", "phone": "2222222222"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["full_name"] == "New Name"
            assert data["phone"] == "2222222222"

    def test_update_profile_no_changes(self, test_app, customer_user, auth_header):
        """Should return current profile if no fields provided."""
        with test_app.test_client() as client:
            response = client.patch(
                "/api/v1/me",
                json={},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["full_name"] == customer_user.full_name
            assert data["phone"] == customer_user.phone


class TestMembershipTier:
    """Tests for POST /api/v1/me/membership"""

    def test_set_membership_premium(self, test_app, customer_user, auth_header, session):
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/me/membership",
                json={"tier": "PREMIUM"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["tier"] == "PREMIUM"
            session.refresh(customer_user)
            assert customer_user.membership_tier == "PREMIUM"

    def test_set_membership_free(self, test_app, customer_user, auth_header, session):
        with test_app.test_client() as client:
            client.post(
                "/api/v1/me/membership",
                json={"tier": "PREMIUM"},
                headers=auth_header(customer_user),
            )
            response = client.post(
                "/api/v1/me/membership",
                json={"tier": "FREE"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["tier"] == "FREE"
            session.refresh(customer_user)
            assert customer_user.membership_tier == "FREE"

    def test_set_membership_invalid_tier(self, test_app, customer_user, auth_header):
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/me/membership",
                json={"tier": "GOLD"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 400

    def test_set_membership_unauthorized(self, test_app):
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/me/membership",
                json={"tier": "PREMIUM"},
            )
            assert response.status_code == 401
