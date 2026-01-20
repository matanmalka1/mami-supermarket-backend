"""Checkout preview and confirmation orchestrator."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models.enums import FulfillmentType
from app.schemas.checkout import (
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    CheckoutPreviewRequest,
    CheckoutPreviewResponse,
)
from app.services.audit_service import AuditService
from app.services.checkout_workflow_service import (
    CheckoutBranchValidator,
    CheckoutCartLoader,
    CheckoutIdempotencyManager,
    CheckoutInventoryManager,
    CheckoutOrderBuilder,
    CheckoutPricing,
)
from app.services.payment_service import PaymentService


class CheckoutService:
    @staticmethod
    def preview(payload: CheckoutPreviewRequest) -> CheckoutPreviewResponse:
        branch_id = CheckoutBranchValidator.resolve_branch(payload.fulfillment_type, payload.branch_id)
        cart = CheckoutCartLoader.load(payload.cart_id)
        inventory = CheckoutInventoryManager(branch_id)
        missing = inventory.missing_items(cart.items)
        totals = CheckoutPricing.calculate(cart, payload.fulfillment_type)
        return CheckoutPreviewResponse(
            cart_total=totals.cart_total,
            delivery_fee=totals.delivery_fee if payload.fulfillment_type == FulfillmentType.DELIVERY else None,
            missing_items=missing,
            fulfillment_type=payload.fulfillment_type,
        )

    @staticmethod
    def confirm(payload: CheckoutConfirmRequest) -> CheckoutConfirmResponse:
        branch_id = CheckoutBranchValidator.resolve_branch(payload.fulfillment_type, payload.branch_id)
        cart = CheckoutCartLoader.load(payload.cart_id, for_update=True)
        CheckoutBranchValidator.validate_delivery_slot(payload.fulfillment_type, payload.delivery_slot_id, branch_id)

        request_hash = CheckoutService._hash_request(payload)
        idempotency_record = CheckoutService._check_idempotency(cart.user_id, payload.idempotency_key, request_hash)
        if idempotency_record:
            if idempotency_record.status_code == 201:
                return CheckoutConfirmResponse.model_validate(idempotency_record.response_payload)
            raise DomainError("IDEMPOTENCY_CONFLICT", "Request payload differs for same Idempotency-Key", status_code=409)

        inventory = CheckoutInventoryManager(branch_id)
        inv_map = inventory.lock_inventory(cart.items)
        missing = inventory.missing_items(cart.items, inv_map)
        if missing:
            raise DomainError(
                "INSUFFICIENT_STOCK",
                "Insufficient stock for items",
                status_code=409,
                details={"missing": [m.model_dump() for m in missing]},
            )

        totals = CheckoutPricing.calculate(cart, payload.fulfillment_type)
        payment_ref: str | None = None
        response_payload: CheckoutConfirmResponse | None = None
        try:
            payment_ref = PaymentService.charge(payload.payment_token_id, float(totals.total_amount))
            order = CheckoutOrderBuilder.create_order(cart, payload, branch_id, totals.total_amount)
            CheckoutOrderBuilder.add_fulfillment_details(order, payload, branch_id)
            inventory.decrement_inventory(cart.items, inv_map)
            CheckoutOrderBuilder.audit_creation(order, totals.total_amount)
            CheckoutService._maybe_save_default_payment_token(cart.user_id, payload.payment_token_id, payload.save_as_default)
            response_payload = CheckoutConfirmResponse(
                order_id=order.id,
                order_number=order.order_number,
                total_paid=Decimal(totals.total_amount),
                payment_reference=payment_ref,
            )
            db.session.commit()
            CheckoutService._store_idempotency(
                user_id=cart.user_id,
                key=payload.idempotency_key,
                request_hash=request_hash,
                response=response_payload,
            )
        except Exception:
            db.session.rollback()
            if payment_ref:
                AuditService.log_event(
                    entity_type="payment",
                    action="PAYMENT_CAPTURED_NOT_COMMITTED",
                    entity_id=cart.id,
                    context={"reference": payment_ref, "cart_id": str(cart.id)},
                )
            raise

        return response_payload

    @staticmethod
    def _hash_request(payload: CheckoutConfirmRequest) -> str:
        return CheckoutIdempotencyManager.hash_request(payload)

    @staticmethod
    def _check_idempotency(user_id: UUID, key: str, request_hash: str):
        return CheckoutIdempotencyManager.get_existing(user_id, key, request_hash)

    @staticmethod
    def _store_idempotency(user_id: UUID, key: str, request_hash: str, response: CheckoutConfirmResponse) -> None:
        CheckoutIdempotencyManager.store_response(user_id, key, request_hash, response)

    @staticmethod
    def _maybe_save_default_payment_token(user_id: UUID, payment_token_id: UUID, save_as_default: bool) -> None:
        if not save_as_default:
            return
        # Placeholder for future default-payment preference persistence.
        AuditService.log_event(
            entity_type="payment_preferences",
            action="SET_DEFAULT",
            actor_user_id=user_id,
            entity_id=payment_token_id,
            new_value={"payment_token_id": str(payment_token_id)},
        )
