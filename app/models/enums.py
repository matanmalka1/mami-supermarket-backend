from __future__ import annotations
from enum import Enum

class Role(str, Enum):
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class MembershipTier(str, Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"

class OrderStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"
    DELAYED = "DELAYED"
    MISSING = "MISSING"

class FulfillmentType(str, Enum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"

class PickedStatus(str, Enum):
    PENDING = "PENDING"
    PICKED = "PICKED"
    MISSING = "MISSING"

class StockRequestType(str, Enum):
    SET_QUANTITY = "SET_QUANTITY"
    ADD_QUANTITY = "ADD_QUANTITY"

class StockRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class CartStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CHECKED_OUT = "CHECKED_OUT"
    ABANDONED = "ABANDONED"

class IdempotencyStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
