from __future__ import annotations
from datetime import time
from uuid import UUID
from pydantic import Field
from .common import DefaultModel, Pagination

class BranchResponse(DefaultModel):
    id: UUID
    name: str
    address: str
    is_active: bool

class DeliverySlotResponse(DefaultModel):
    id: UUID
    branch_id: UUID
    day_of_week: int
    start_time: time
    end_time: time

class InventoryResponse(DefaultModel):
    id: UUID
    branch_id: UUID
    branch_name: str
    product_id: UUID
    product_name: str
    available_quantity: int
    reserved_quantity: int
    limit: int
    offset: int
    total: int

class InventoryListResponse(DefaultModel):
    items: list[InventoryResponse]
    pagination: Pagination

class InventoryUpdateRequest(DefaultModel):
    available_quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)

class BranchAdminRequest(DefaultModel):
    name: str
    address: str

class DeliverySlotAdminRequest(DefaultModel):
    branch_id: UUID
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
