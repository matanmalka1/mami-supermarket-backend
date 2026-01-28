"""Tests for public branches endpoints."""

from app.models import Branch

class TestListBranches:
    """Tests for GET /api/v1/branches"""

    def test_list_branches_success(self, test_app, session):
        """Should list all active branches."""
        # Create additional branch
        branch = Branch(name="Test Branch", address="123 Test St", is_active=True)
        session.add(branch)
        session.commit()

        with test_app.test_client() as client:
            response = client.get("/api/v1/branches")
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert isinstance(data, list)
            assert len(data) >= 1  # At least the test branch we just created

    def test_list_branches_pagination(self, test_app, session):
        """Should respect pagination parameters."""
        with test_app.test_client() as client:
            response = client.get("/api/v1/branches?limit=1&offset=0")
            assert response.status_code == 200
            data = response.get_json()
            assert "pagination" in data
            assert data["pagination"]["limit"] == 1


class TestListDeliverySlots:
    """Tests for GET /api/v1/delivery-slots"""

    def test_list_all_slots(self, test_app, session):
        """Should list all delivery slots."""
        with test_app.test_client() as client:
            response = client.get("/api/v1/delivery-slots")
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert isinstance(data, list)

    def test_filter_by_day_of_week(self, test_app, session):
        """Should filter slots by day of week."""
        with test_app.test_client() as client:
            response = client.get("/api/v1/delivery-slots?dayOfWeek=0")
            assert response.status_code == 200
            data = response.get_json()["data"]
            for slot in data:
                assert slot["day_of_week"] == 0

    def test_filter_by_branch(self, test_app, session):
        """Should filter slots by branch."""
        branch = session.query(Branch).first()
        with test_app.test_client() as client:
            response = client.get(f"/api/v1/delivery-slots?branchId={branch.id}")
            assert response.status_code == 200
            data = response.get_json()["data"]
            for slot in data:
                assert slot["branch_id"] == branch.id
