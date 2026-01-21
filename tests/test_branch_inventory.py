from app.models import Branch, Category, Inventory, Product
from app.schemas.branches import InventoryUpdateRequest
from app.services.branch_service import BranchService
from app.services.inventory_service import InventoryService


def test_ensure_delivery_source_branch_exists(test_app):
    with test_app.app_context():
        branch = BranchService.ensure_delivery_source_branch_exists(test_app.config["DELIVERY_SOURCE_BRANCH_ID"])
    assert branch.name == "Warehouse"


def test_inventory_update_changes_quantities(session, product_with_inventory):
    product, inv, _ = product_with_inventory
    payload = InventoryUpdateRequest(available_quantity=5, reserved_quantity=1)
    updated = InventoryService.update_inventory(inv.id, payload)
    assert updated.available_quantity == 5
    assert updated.reserved_quantity == 1
    # ensure response carries names from relationships
    assert updated.product_name and updated.branch_name
