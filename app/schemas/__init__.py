"""API DTO package."""

from .auth import AuthResponse, ChangePasswordRequest, LoginRequest, RegisterRequest, UserResponse
from .audit import AuditQuery, AuditResponse
from .cart import CartItemResponse, CartItemUpsertRequest, CartResponse
from .branches import (
    BranchAdminRequest,
    BranchResponse,
    DeliverySlotAdminRequest,
    DeliverySlotResponse,
    InventoryListResponse,
    InventoryResponse,
    InventoryUpdateRequest,
)
from .catalog import (
    AutocompleteItem,
    AutocompleteResponse,
    CategoryAdminRequest,
    CategoryResponse,
    ProductAdminRequest,
    ProductResponse,
    ProductSearchResponse,
    ProductUpdateRequest,
)
from .checkout import (
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    CheckoutPreviewRequest,
    CheckoutPreviewResponse,
)
from .common import DefaultModel, ErrorResponse, PaginatedResponse, Pagination
from .orders import CancelOrderResponse, OrderListResponse, OrderResponse
from .ops import OpsOrderResponse, OpsOrdersQuery, UpdateOrderStatusRequest, UpdatePickStatusRequest
from .stock_requests import (
    BulkReviewItem,
    BulkReviewRequest,
    StockRequestCreateRequest,
    StockRequestResponse,
    StockRequestReviewRequest,
)

__all__ = [
    "DefaultModel",
    "ErrorResponse",
    "Pagination",
    "PaginatedResponse",
    "RegisterRequest",
    "LoginRequest",
    "ChangePasswordRequest",
    "UserResponse",
    "AuthResponse",
    "CategoryResponse",
    "BranchAdminRequest",
    "BranchResponse",
    "DeliverySlotAdminRequest",
    "DeliverySlotResponse",
    "InventoryListResponse",
    "InventoryResponse",
    "InventoryUpdateRequest",
    "ProductResponse",
    "ProductSearchResponse",
    "ProductUpdateRequest",
    "AutocompleteItem",
    "AutocompleteResponse",
    "CategoryAdminRequest",
    "ProductAdminRequest",
    "CartItemUpsertRequest",
    "CartItemResponse",
    "CartResponse",
    "CheckoutPreviewRequest",
    "CheckoutPreviewResponse",
    "CheckoutConfirmRequest",
    "CheckoutConfirmResponse",
    "OrderItemResponse",
    "OrderResponse",
    "OrderListResponse",
    "CancelOrderResponse",
    "OpsOrdersQuery",
    "OpsOrderResponse",
    "UpdatePickStatusRequest",
    "UpdateOrderStatusRequest",
    "StockRequestCreateRequest",
    "StockRequestReviewRequest",
    "BulkReviewRequest",
    "BulkReviewItem",
    "StockRequestResponse",
    "AuditQuery",
    "AuditResponse",
]
