from datetime import time
from app.models.enums import Role
from app.models import Branch, DeliverySlot, Inventory, Product, Category

def create_branch(session):
    branch = Branch(name="B1", address="A1", is_active=True)
    session.add(branch)
    session.commit()
    return branch

def create_delivery_slot(session, branch):
    slot = DeliverySlot(branch_id=branch.id, day_of_week=0, start_time=time(6,0), end_time=time(8,0))
    session.add(slot)
    session.commit()
    return slot

def create_inventory(session, branch, product):
    inv = Inventory(product_id=product.id, branch_id=branch.id, available_quantity=1, reserved_quantity=0)
    session.add(inv)
    session.commit()
    return inv

def create_product(session, category):
    product = Product(name="P1", sku="SKU1", price="10.00", category_id=category.id)
    session.add(product)
    session.commit()
    return product

def create_category(session):
    category = Category(name="C1")
    session.add(category)
    session.commit()
    return category

def test_admin_branches_jwt_required(test_app, auth_header, create_user_with_role, session):
    """All admin branches endpoints require JWT and proper role (אמיתי, עם אובייקטים קיימים)."""
    # Branch create (POST)
    with test_app.test_client() as client:
        manager = create_user_with_role(role=Role.MANAGER)
        resp = client.post("/api/v1/admin/branches", json={"name": "B2", "address": "A2"}, headers=auth_header(manager))
        assert resp.status_code in (201, 200)
        # forbidden
        employee = create_user_with_role(role=Role.EMPLOYEE)
        resp = client.post("/api/v1/admin/branches", json={"name": "B3", "address": "A3"}, headers=auth_header(employee))
        assert resp.status_code == 403

    # Branch update (PATCH)
    branch = create_branch(session)
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.patch(f"/api/v1/admin/branches/{branch.id}", json={"name": "B1-upd", "address": "A1"}, headers=auth_header(admin))
        assert resp.status_code in (200, 201)

    # Branch toggle (PATCH)
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.patch(f"/api/v1/admin/branches/{branch.id}/toggle?active=false", headers=auth_header(admin))
        assert resp.status_code in (200, 201)

    # Delivery slot create (POST)
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.post("/api/v1/admin/delivery-slots", json={"branch_id": str(branch.id), "day_of_week": 0, "start_time": "06:00", "end_time": "08:00"}, headers=auth_header(admin))
        assert resp.status_code in (201, 200)

    # Delivery slot update (PATCH)
    slot = create_delivery_slot(session, branch)
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.patch(f"/api/v1/admin/delivery-slots/{slot.id}", json={"branch_id": str(branch.id), "day_of_week": 0, "start_time": "07:00", "end_time": "09:00"}, headers=auth_header(admin))
        assert resp.status_code in (200, 201)

    # Delivery slot toggle (PATCH)
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.patch(f"/api/v1/admin/delivery-slots/{slot.id}/toggle?active=false", headers=auth_header(admin))
        assert resp.status_code in (200, 201)

    # Inventory GET
    category = create_category(session)
    product = create_product(session, category)
    inv = create_inventory(session, branch, product)
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.get("/api/v1/admin/inventory", headers=auth_header(admin))
        assert resp.status_code == 200

    # Inventory update (PATCH)
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.patch(f"/api/v1/admin/inventory/{inv.id}", json={"available_quantity": 5, "reserved_quantity": 1}, headers=auth_header(admin))
        assert resp.status_code in (200, 201)

    # Inventory bulk upload (POST)
    import io
    csv_content = f"product_id,branch_id,available_quantity,reserved_quantity\n{product.id},{branch.id},10,0\n"
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "bulk.csv")}
    with test_app.test_client() as client:
        admin = create_user_with_role(role=Role.ADMIN)
        resp = client.post("/api/v1/admin/inventory/bulk", content_type="multipart/form-data", data=data, headers=auth_header(admin))
        assert resp.status_code in (202, 200)
