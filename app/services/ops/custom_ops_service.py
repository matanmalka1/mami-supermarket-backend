from datetime import datetime, timezone

from app.services.ops.performance_service import OpsPerformanceService

def create_batch_for_ops(user_id, batch_payload):
    created_at = datetime.now(timezone.utc)
    batch_id = int(created_at.timestamp() * 1_000)
    return {"id": batch_id, "created_by": user_id, "payload": batch_payload}

def get_ops_performance(user_id):
    metrics = OpsPerformanceService.compute_metrics()
    metrics["user_id"] = user_id
    return metrics


def get_ops_alerts(user_id):
    now = datetime.now(timezone.utc)
    created = now.isoformat()
    return [
        {
            "id": f"alert-{user_id}-1",
            "text": "Realtime batch queue has pending orders",
            "type": "info",
            "severity": "medium",
            "createdAt": created,
            "time": created,
        },
        {
            "id": f"alert-{user_id}-2",
            "text": "Inventory sync lag detected",
            "type": "alert",
            "severity": "high",
            "createdAt": created,
            "time": created,
        },
    ]
