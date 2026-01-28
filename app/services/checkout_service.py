"""Checkout preview and confirmation orchestrator."""

from __future__ import annotations

from decimal import Decimal
import traceback
from flask import current_app

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models.enums import FulfillmentType
from app.schemas.checkout import (
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    CheckoutPreviewRequest,
    CheckoutPreviewResponse,
)
from app.models.payment_token import PaymentToken
from app.services.audit_service import AuditService
from app.services.checkout import (
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
    def confirm(payload: CheckoutConfirmRequest, idempotency_key: str) -> tuple[CheckoutConfirmResponse, bool]:
        branch_id = CheckoutBranchValidator.resolve_branch(payload.fulfillment_type, payload.branch_id)
        cart = CheckoutCartLoader.load(payload.cart_id, for_update=True)
        CheckoutBranchValidator.validate_delivery_slot(payload.fulfillment_type, payload.delivery_slot_id, branch_id)

        request_hash = CheckoutService._hash_request(payload)
        
        # Check or create IN_PROGRESS idempotency record
        idempotency_record, is_new = CheckoutIdempotencyManager.get_or_create_in_progress(
            cart.user_id, idempotency_key, request_hash
        )
        
        # If not new, return cached response (SUCCEEDED status) with 200 status
        if not is_new:
            return CheckoutConfirmResponse.model_validate(idempotency_record.response_payload), False

        inventory = CheckoutInventoryManager(branch_id)
        inv_map = inventory.lock_inventory(cart.items)
        missing = inventory.missing_items(cart.items, inv_map)
        if missing:
            CheckoutIdempotencyManager.mark_failed(idempotency_record)
            db.session.commit()
            raise DomainError(
                "INSUFFICIENT_STOCK",
                "Insufficient stock for items",
                status_code=409,
                details={"missing": [m.model_dump() for m in missing]},
            )

        totals = CheckoutPricing.calculate(cart, payload.fulfillment_type)
        payment_ref: str | None = None
        response_payload: CheckoutConfirmResponse | None = None
        order = None
        try:
            order = CheckoutOrderBuilder.create_order(cart, payload, branch_id, totals.total_amount)
            CheckoutOrderBuilder.add_fulfillment_details(order, payload, branch_id)
            inventory.decrement_inventory(cart.items, inv_map)
            CheckoutOrderBuilder.audit_creation(order, totals.total_amount)
            payment_ref = PaymentService.charge(payload.payment_token_id, float(totals.total_amount))
            CheckoutService._maybe_save_default_payment_token(cart.user_id, payload.payment_token_id, payload.save_as_default)

            response_payload = CheckoutConfirmResponse(
                order_id=order.id,
                order_number=order.order_number,
                total_paid=Decimal(totals.total_amount),
                payment_reference=payment_ref,
            )

            # Mark idempotency as succeeded
            CheckoutIdempotencyManager.mark_succeeded(idempotency_record, response_payload, order.id)

            db.session.commit()
        except DomainError:
            db.session.rollback()
            raise
        except Exception as exc:
            db.session.rollback()
            if payment_ref:
                AuditService.log_event(
                    entity_type="payment",
                    action="PAYMENT_CAPTURED_NOT_COMMITTED",
                    entity_id=cart.id,
                    context={"reference": payment_ref, "cart_id": str(cart.id)},
                )
            print("CheckoutService.confirm unexpected error:", exc)
            traceback.print_exc()
            current_app.logger.exception(
                "Unexpected error confirming checkout for cart %s",
                cart.id,
            )
            raise

        return response_payload, True  # is_new=True for newly created orders

    @staticmethod
    def _hash_request(payload: CheckoutConfirmRequest) -> str:
        return CheckoutIdempotencyManager.hash_request(payload)

    @staticmethod
    def _maybe_save_default_payment_token(user_id: int, payment_token_id: int, save_as_default: bool) -> None:
        if not save_as_default:
            return
        db.session.execute(
            PaymentToken.__table__.update()
            .where(PaymentToken.user_id == user_id)
            .values(is_default=False)
        )
        token = db.session.get(PaymentToken, payment_token_id)
        if token and token.user_id == user_id:
            token.is_default = True
            db.session.add(token)
        AuditService.log_event(
            entity_type="payment_preferences",
            action="SET_DEFAULT",
            actor_user_id=user_id,
            entity_id=payment_token_id,
            new_value={"payment_token_id": str(payment_token_id)},
        )
