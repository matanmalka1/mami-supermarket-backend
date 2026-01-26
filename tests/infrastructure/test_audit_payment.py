from app.services.audit_service import AuditQueryService, AuditService
from app.services.payment_service import PaymentService
from app.extensions import db


def test_audit_log_event_persists(session):
    AuditService.log_event(entity_type="test", action="CREATE", entity_id=1, context={"foo": "bar"})
    db.session.commit()
    rows, total = AuditQueryService.list_logs(filters={}, limit=10, offset=0)
    assert total == 1
    assert rows[0]["context"] == {"foo": "bar"}


def test_payment_charge_returns_reference():
    ref = PaymentService.charge(payment_token_id=0, amount=10.0)
    assert ref.startswith("pay_")
