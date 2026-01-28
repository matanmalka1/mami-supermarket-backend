
def test_category_list_includes_description(client, session):
    resp = client.get("/api/v1/catalog/categories")
    data = resp.get_json()["data"] if "data" in resp.get_json() else resp.get_json()
    assert isinstance(data, list)
    assert all("description" in c for c in data)
    assert all("icon_slug" in c for c in data)

def test_product_detail_includes_new_fields(client, session):
    resp = client.get("/api/v1/catalog/products/search?limit=1")
    prod = resp.get_json()["data"][0]
    prod_id = prod["id"]
    resp2 = client.get(f"/api/v1/catalog/products/{prod_id}")
    detail = resp2.get_json()["data"] if "data" in resp2.get_json() else resp2.get_json()
    for field in ["old_price", "unit", "nutritional_info", "is_organic", "bin_location", "image_url"]:
        assert field in detail

def test_search_filters_min_max_price(client, session):
    resp = client.get("/api/v1/catalog/products/search?min_price=10&max_price=12")
    data = resp.get_json()["data"]
    assert all(10 <= float(p["price"]) <= 12 for p in data)

def test_search_filter_organic_only(client, session):
    resp = client.get("/api/v1/catalog/products/search?organic_only=true")
    data = resp.get_json()["data"]
    assert all(p["is_organic"] for p in data)

def test_search_filters_combined(client, session):
    resp = client.get("/api/v1/catalog/products/search?min_price=5&max_price=20&organic_only=true")
    data = resp.get_json()["data"]
    assert all(5 <= float(p["price"]) <= 20 and p["is_organic"] for p in data)

def test_search_pagination_meta(client, session):
    resp = client.get("/api/v1/catalog/products/search?limit=2&offset=0")
    meta = resp.get_json()["meta"]
    assert "total" in meta and "limit" in meta and "offset" in meta and "has_next" in meta

def test_featured_endpoint(client, session):
    resp = client.get("/api/v1/catalog/products/featured?limit=3")
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) <= 3
    for p in data:
        assert "id" in p and "name" in p

def test_admin_analytics_revenue_requires_admin(client, session):
    resp = client.get("/api/v1/admin/analytics/revenue")
    assert resp.status_code in (401, 403)

def test_admin_analytics_revenue_shape(client, session, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/v1/admin/analytics/revenue?range=30d", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "labels" in data and "values" in data
    assert len(data["labels"]) == len(data["values"])

def test_admin_analytics_revenue_empty_returns_arrays(client, session, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/v1/admin/analytics/revenue?range=30d", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data.get("labels"), list)
    assert isinstance(data.get("values"), list)
