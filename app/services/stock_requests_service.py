"""Aggregate exports for stock request services (employee/admin)."""

from app.services.stock_requests import StockRequestEmployeeService, StockRequestReviewService
from app.services.stock_requests.ops_service import list_ops

class StockRequestService:
    create_request = staticmethod(StockRequestEmployeeService.create_request)
    list_my = staticmethod(StockRequestEmployeeService.list_my)
    list_admin = staticmethod(StockRequestReviewService.list_admin)
    get_request = staticmethod(StockRequestReviewService.get_request)
    review = staticmethod(StockRequestReviewService.review)
    bulk_review = staticmethod(StockRequestReviewService.bulk_review)
    list_ops = staticmethod(list_ops)


__all__ = ["StockRequestService", "StockRequestEmployeeService", "StockRequestReviewService"]
