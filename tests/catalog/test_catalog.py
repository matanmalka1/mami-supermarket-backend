import pytest

from app.middleware.error_handler import DomainError
from app.services.catalog import CatalogAdminService, CatalogQueryService


def test_product_toggle_disables_access(session):
    category = CatalogAdminService.create_category("Dairy", "Milk products")
    product = CatalogAdminService.create_product(
        name="Yogurt",
        sku="YG1",
        price="4.50",
        category_id=category.id,
        description=None,
    )
    CatalogAdminService.toggle_product(product.id, active=False)
    with pytest.raises(DomainError) as exc:
        CatalogQueryService.get_product(product.id, branch_id=None)
    assert exc.value.code == "NOT_FOUND"


def test_search_in_stock_filters_by_branch(session, product_with_inventory):
    product, inv, other_branch = product_with_inventory
    product.is_active = True
    inv.available_quantity = 2
    session.add_all([product, inv])
    session.commit()
    items, total = CatalogQueryService.search_products(
        query=None, category_id=None, in_stock=True, branch_id=inv.branch_id, limit=10, offset=0
    )
    assert total >= 1
    assert any(p.id == product.id for p in items)

    items_empty, total_empty = CatalogQueryService.search_products(
        query=None, category_id=None, in_stock=True, branch_id=other_branch.id, limit=10, offset=0
    )
    assert total_empty == 0
    assert items_empty == []
