"""Aggregate exports for ops order services (queries and updates)."""

from app.services.ops import OpsOrderQueryService, OpsOrderUpdateService

# Backwards-compatible facade
class OpsOrderService:
    list_orders = staticmethod(OpsOrderQueryService.list_orders)
    get_order = staticmethod(OpsOrderQueryService.get_order)
    update_item_status = staticmethod(OpsOrderUpdateService.update_item_status)
    update_order_status = staticmethod(OpsOrderUpdateService.update_order_status)


__all__ = ["OpsOrderService", "OpsOrderQueryService", "OpsOrderUpdateService"]
