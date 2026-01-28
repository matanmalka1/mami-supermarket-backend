from __future__ import annotations
from app.models import Order
from app.models.enums import OrderStatus, PickedStatus, Role


def can_transition(order: Order, new_status: OrderStatus, actor_role: Role) -> bool:
    if actor_role not in {Role.EMPLOYEE, Role.MANAGER, Role.ADMIN}:
        return False
    return _basic_transition_allowed(order, new_status)


def _basic_transition_allowed(order: Order, new_status: OrderStatus) -> bool:
    current = order.status
    if current == OrderStatus.CREATED and new_status == OrderStatus.IN_PROGRESS:
        return True
    if current == OrderStatus.IN_PROGRESS and new_status == OrderStatus.READY:
        all_picked = all(item.picked_status == PickedStatus.PICKED for item in order.items)
        return all_picked
    if current == OrderStatus.IN_PROGRESS and new_status == OrderStatus.MISSING:
        any_missing = any(item.picked_status == PickedStatus.MISSING for item in order.items)
        return any_missing
    return False
