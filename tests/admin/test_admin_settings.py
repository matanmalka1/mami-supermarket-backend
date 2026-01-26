from app.models.enums import Role

def test_admin_settings_get(test_app, auth_header, create_user_with_role):
    """GET /api/v1/admin/settings returns settings envelope for admin only (אמיתי)."""
    admin = create_user_with_role(role=Role.ADMIN)
    with test_app.test_client() as client:
        response = client.get(
            "/api/v1/admin/settings",
            headers=auth_header(admin),
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert "delivery_min" in data
        assert "delivery_fee" in data
        assert "slots" in data

    # forbidden for non-admin
    employee = create_user_with_role(role=Role.EMPLOYEE)
    with test_app.test_client() as client:
        response = client.get(
            "/api/v1/admin/settings",
            headers=auth_header(employee),
        )
        assert response.status_code == 403
