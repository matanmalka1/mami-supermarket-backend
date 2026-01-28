import json

def test_health_not_limited(test_app):
    client = test_app.test_client()
    for _ in range(10):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

def test_login_rate_limited(test_app, session, users):
    client = test_app.test_client()
    user, _ = users
    for _ in range(5):
        resp = client.post("/api/v1/auth/login", json={"email": user.email, "password": "badpass"})

    resp = client.post("/api/v1/auth/login", json={"email": user.email, "password": "badpass"})
    assert resp.status_code == 429
    data = json.loads(resp.data)
    assert data["error"]["code"] in {"HTTP_ERROR", "AUTH_ERROR"}
    assert "error" in data
