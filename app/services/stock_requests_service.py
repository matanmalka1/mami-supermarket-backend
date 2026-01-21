"""Aggregate exports for stock request services (employee/admin)."""

from app.services.stock_requests import StockRequestEmployeeService, StockRequestReviewService

# Backwards-compatible facade
class StockRequestService:
    create_request = staticmethod(StockRequestEmployeeService.create_request)
    list_my = staticmethod(StockRequestEmployeeService.list_my)
    list_admin = staticmethod(StockRequestReviewService.list_admin)
    review = staticmethod(StockRequestReviewService.review)
    bulk_review = staticmethod(StockRequestReviewService.bulk_review)


__all__ = ["StockRequestService", "StockRequestEmployeeService", "StockRequestReviewService"]
