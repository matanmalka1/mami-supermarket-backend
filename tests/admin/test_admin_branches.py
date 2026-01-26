"""Tests for admin branch management endpoints."""

from app.models import  Branch, Inventory, Product, Category
from app.models.enums import Role

class TestBranchManagement:
    """Tests for branch CRUD"""

    def test_create_branch(self, test_app, auth_header, create_user_with_role):
        """Should create a new branch (אמיתי)."""
        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/admin/branches",
                json={"name": "New Branch", "address": "456 New St"},
                headers=auth_header(admin),
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["name"] == "New Branch"
            assert data["address"] == "456 New St"

    def test_update_branch(self, test_app, auth_header, create_user_with_role, session):
        """Should update branch details."""
        branch = Branch(name="Old Branch", address="Old Address", is_active=True)
        session.add(branch)
        session.commit()

        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/branches/{branch.id}",
                json={"name": "Updated Branch", "address": "Old Address"},
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["name"] == "Updated Branch"

    def test_toggle_branch(self, test_app, auth_header, create_user_with_role, session):
        """Should toggle branch active status."""
        branch = Branch(name="Test", address="Test St", is_active=True)
        session.add(branch)
        session.commit()

        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/branches/{branch.id}/toggle?active=false",
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is False


class TestInventoryManagement:
    """Tests for inventory management"""

    def test_update_inventory(self, test_app, auth_header, create_user_with_role, session):
        """Should update inventory quantity (אמיתי)."""
        category = Category(name="Cat", description="Test")
        session.add(category)
        session.flush()
        product = Product(name="Test", sku="SKU1", price="10.00", category_id=category.id)
        branch = Branch(name="Branch", address="Addr", is_active=True)
        session.add_all([product, branch])
        session.flush()
        inventory = Inventory(product_id=product.id, branch_id=branch.id, available_quantity=10)
        session.add(inventory)
        session.commit()

        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/inventory/{inventory.id}",
                json={"available_quantity": 50, "reserved_quantity": 0},
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["available_quantity"] == 50
