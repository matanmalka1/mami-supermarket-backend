from __future__ import annotations
from datetime import time

from pydantic import Field
from .common import DefaultModel, Pagination

class BranchResponse(DefaultModel):
    id: int
    name: str
    address: str
    is_active: bool

class DeliverySlotResponse(DefaultModel):
    id: int
    branch_id: int
    day_of_week: int
    start_time: time
    end_time: time

class InventoryResponse(DefaultModel):
    id: int
    branch_id: int
    branch_name: str
    product_id: int
    product_name: str
    product_sku: str
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

class InventoryCreateRequest(DefaultModel):
    product_id: int
    branch_id: int
    available_quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)

class BranchAdminRequest(DefaultModel):
    name: str
    address: str

class DeliverySlotAdminRequest(DefaultModel):
    branch_id: int
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
