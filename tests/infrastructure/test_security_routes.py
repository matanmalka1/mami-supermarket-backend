from flask import json
from flask_jwt_extended import create_access_token

from app.models import User
from app.models.enums import Role

def _auth_header_for(app, user_id, role):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"role": role.value})
    return {"Authorization": f"Bearer {token}"}

def test_admin_route_requires_role(test_app, session):
    employee = User(email="emp@example.com", full_name="Emp", password_hash="x", role=Role.EMPLOYEE)
    session.add(employee)
    session.commit()
    client = test_app.test_client()
    resp = client.post(
        "/api/v1/admin/branches",
        json={"name": "AdminBranch", "address": "Addr"},
        headers=_auth_header_for(test_app, employee.id, employee.role),
    )
    assert resp.status_code == 403
    data = json.loads(resp.data)
    assert data["error"]["code"] == "AUTHORIZATION_ERROR"


def test_admin_route_allows_manager(test_app, session):
    manager = User(email="mgr@example.com", full_name="Mgr", password_hash="x", role=Role.MANAGER)
    session.add(manager)
    session.commit()
    client = test_app.test_client()
    resp = client.post(
        "/api/v1/admin/branches",
        json={"name": "AdminBranch2", "address": "Addr"},
        headers=_auth_header_for(test_app, manager.id, manager.role),
    )
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert data["data"]["name"] == "AdminBranch2"
