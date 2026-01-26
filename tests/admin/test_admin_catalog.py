"""Tests for admin catalog management endpoints."""

from app.models import Category, Product
from app.models.enums import Role
import secrets


class TestCategoryManagement:
    """Tests for category CRUD"""

    def test_create_category(self, test_app, auth_header, create_user_with_role):
        """Should create a new category (אמיתי)."""
        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/admin/categories",
                json={"name": "New Category", "description": "Test category"},
                headers=auth_header(admin),
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["name"] == "New Category"

    def test_update_category(self, test_app, auth_header, create_user_with_role, session):
        """Should update category details."""
        category = Category(name="Old Name", description="Old desc")
        session.add(category)
        session.commit()

        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/categories/{category.id}",
                json={"name": "Updated Name", "description": "Updated desc"},
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["name"] == "Updated Name"

    def test_toggle_category(self, test_app, auth_header, create_user_with_role, session):
        """Should toggle category active status."""
        category = Category(name="Test", description="Test", is_active=True)
        session.add(category)
        session.commit()

        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/categories/{category.id}/toggle?active=false",
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is False


class TestProductManagement:
    """Tests for product CRUD"""

    def test_create_product(self, test_app, auth_header, create_user_with_role, session):
        """Should create a new product."""
        category = Category(name="Test Cat", description="Test")
        session.add(category)
        session.commit()

        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            unique_sku = f"SKU-{secrets.token_hex(4)}"
            response = client.post(
                "/api/v1/admin/products",
                json={
                    "name": "New Product",
                    "sku": unique_sku,
                    "price": 99.99,
                    "category_id": str(category.id),
                    "description": "Test product",
                },
                headers=auth_header(admin),
            )
            if response.status_code != 201:
                print("RESPONSE JSON:", response.get_json())
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["name"] == "New Product"
            assert data["sku"] == unique_sku

    def test_update_product(self, test_app, auth_header, create_user_with_role, session):
        """Should update product details."""
        category = Category(name="Cat", description="Test")
        session.add(category)
        session.flush()
        product = Product(
            name="Old Product",
            sku="OLD123",
            price="50.00",
            category_id=category.id,
        )
        session.add(product)
        session.commit()

        admin = create_user_with_role(role=Role.ADMIN)
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/products/{product.id}",
                json={"name": "Updated Product", "price": 75.50},
                headers=auth_header(admin),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["name"] == "Updated Product"
