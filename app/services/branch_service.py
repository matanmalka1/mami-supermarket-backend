"""Aggregate exports for branch and delivery slot services."""

from app.services.branch import BranchCoreService, DeliverySlotService

# Backwards-compatible facade
class BranchService:
    ensure_delivery_source_branch_exists = staticmethod(BranchCoreService.ensure_delivery_source_branch_exists)
    list_branches = staticmethod(BranchCoreService.list_branches)
    create_branch = staticmethod(BranchCoreService.create_branch)
    update_branch = staticmethod(BranchCoreService.update_branch)
    toggle_branch = staticmethod(BranchCoreService.toggle_branch)
    list_delivery_slots = staticmethod(DeliverySlotService.list_delivery_slots)
    create_delivery_slot = staticmethod(DeliverySlotService.create_delivery_slot)
    update_delivery_slot = staticmethod(DeliverySlotService.update_delivery_slot)
    toggle_delivery_slot = staticmethod(DeliverySlotService.toggle_delivery_slot)


__all__ = ["BranchService", "BranchCoreService", "DeliverySlotService"]
