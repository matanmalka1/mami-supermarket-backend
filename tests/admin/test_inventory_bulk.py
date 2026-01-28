import io
from app.models.enums import Role


def test_admin_inventory_bulk_upload(test_app, auth_header, create_user_with_role, session):
    """POST /api/v1/admin/inventory/bulk uploads CSV and returns summary envelope (אמיתי)."""
    from app.models import Branch, Product, Category
    branch = Branch(name="BulkBranch", address="BulkAddr", is_active=True)
    session.add(branch)
    category = Category(name="BulkCat")
    session.add(category)
    session.flush()
    product1 = Product(name="BulkP1", sku="BULKSKU1", price="10.00", category_id=category.id)
    product2 = Product(name="BulkP2", sku="BULKSKU2", price="20.00", category_id=category.id)
    session.add_all([product1, product2])
    session.commit()
    csv_content = (
        f"product_id,branch_id,available_quantity,reserved_quantity\n"
        f"{product1.id},{branch.id},10,0\n"
        f"{product2.id},{branch.id},5,1\n"
        f"bad,{branch.id},notanint,0\n"
    )
    data = {
        "file": (io.BytesIO(csv_content.encode("utf-8")), "bulk.csv")
    }
    admin = create_user_with_role(role=Role.ADMIN)
    with test_app.test_client() as client:
        response = client.post(
            "/api/v1/admin/inventory/bulk",
            content_type="multipart/form-data",
            data=data,
            headers=auth_header(admin),
        )
        assert response.status_code == 202
        data = response.get_json()["data"]
        assert data["total"] == 3
        assert data["success"] == 2
        assert data["errors"] == 1
        assert len(data["error_details"]) == 1
        assert any(r["status"] == "error" for r in data["results"])

    # forbidden for non-manager/admin
    employee = create_user_with_role(role=Role.EMPLOYEE)
    with test_app.test_client() as client:
        response = client.post(
            "/api/v1/admin/inventory/bulk",
            content_type="multipart/form-data",
            data=data,
            headers=auth_header(employee),
        )
        assert response.status_code == 403
