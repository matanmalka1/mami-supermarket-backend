"""Tests for admin user management endpoints."""

from app.models.enums import Role

class TestListUsers:
    def test_list_users_success(self, test_app, auth_header, create_user_with_role, session):
        """Should list all users with pagination (אמיתי)."""
        admin = create_user_with_role(role=Role.ADMIN)
        customers = [create_user_with_role(role=Role.CUSTOMER) for _ in range(3)]
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users",
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "data" in data
            assert "total" in data
            assert data["total"] >= 4

    def test_list_users_filter_by_role(self, test_app, auth_header, create_user_with_role, session):
        """Should filter users by role."""
        admin = create_user_with_role(role=Role.ADMIN)
        customers = [create_user_with_role(role=Role.CUSTOMER) for _ in range(3)]
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users?role=CUSTOMER",
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert all(user["role"] == "CUSTOMER" for user in data)

    def test_list_users_search(self, test_app, auth_header, create_user_with_role, session):
        """Should search users by email or name."""
        admin = create_user_with_role(role=Role.ADMIN)
        customers = [create_user_with_role(role=Role.CUSTOMER) for _ in range(3)]
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users?q=customer",
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert len(data) >= 1
            assert any("customer" in user["email"] for user in data)

    def test_list_users_requires_admin(self, test_app, auth_header, create_user_with_role):
        """Should require admin/manager role."""
        customer = create_user_with_role(role=Role.CUSTOMER)
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users",
                headers=auth_header(customer),
            )
            assert response.status_code == 403


class TestGetUser:
    """Tests for GET /api/v1/admin/users/{user_id}"""

    def test_get_user_success(self, test_app, auth_header, create_user_with_role, session):
        """Should get user details."""
        admin = create_user_with_role(role=Role.ADMIN)
        target_user = create_user_with_role(role=Role.CUSTOMER)
        with test_app.test_client() as client:
            response = client.get(
                f"/api/v1/admin/users/{target_user.id}",
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["id"] == str(target_user.id)
            assert data["email"] == target_user.email

    def test_get_user_not_found(self, test_app, auth_header, create_user_with_role):
        """Should return 404 for non-existent user."""
        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.get(
                f"/api/v1/admin/users/9999",
                headers=auth_header(admin),
            )
            assert response.status_code == 404


class TestUpdateUser:
    """Tests for PATCH /api/v1/admin/users/{user_id}"""

    def test_update_user_role(self, test_app, auth_header, create_user_with_role, session):
        """Should update user role."""
        admin = create_user_with_role(role=Role.ADMIN)
        target_user = create_user_with_role(role=Role.CUSTOMER)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{target_user.id}",
                json={"role": "EMPLOYEE"},
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["role"] == "EMPLOYEE"
            session.refresh(target_user)
            assert target_user.role == Role.EMPLOYEE

    def test_update_user_deactivate(self, test_app, auth_header, create_user_with_role, session):
        """Should deactivate user."""
        admin = create_user_with_role(role=Role.ADMIN)
        target_user = create_user_with_role(role=Role.CUSTOMER)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{target_user.id}",
                json={"is_active": False},
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is False

    def test_cannot_modify_own_role(self, test_app, auth_header, create_user_with_role):
        """Should prevent admin from changing their own role."""
        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{admin.id}",
                json={"role": "CUSTOMER"},
                headers=auth_header(admin),
            )
            assert response.status_code == 403
            assert "CANNOT_MODIFY_SELF_ROLE" in response.get_json()["error"]["code"]


class TestToggleUser:
    """Tests for PATCH /api/v1/admin/users/{user_id}/toggle"""

    def test_toggle_user_activate(self, test_app, auth_header, create_user_with_role, session):
        """Should toggle user active status."""
        admin = create_user_with_role(role=Role.ADMIN)
        target_user = create_user_with_role(role=Role.CUSTOMER)
        target_user.is_active = False
        session.commit()
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{target_user.id}/toggle?active=true",
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is True

    def test_cannot_deactivate_self(self, test_app, auth_header, create_user_with_role):
        """Should prevent admin from deactivating themselves."""
        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{admin.id}/toggle?active=false",
                headers=auth_header(admin),
            )
            assert response.status_code == 403
            assert "CANNOT_DEACTIVATE_SELF" in response.get_json()["error"]["code"]

    def test_toggle_missing_param(self, test_app, auth_header, create_user_with_role, session):
        """Should require active query parameter."""
        admin = create_user_with_role(role=Role.ADMIN)
        target_user = create_user_with_role(role=Role.CUSTOMER)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{target_user.id}/toggle",
                headers=auth_header(admin),
            )
            assert response.status_code == 400
