from datetime import datetime
from uuid import uuid4

from app.services.ops.performance_service import OpsPerformanceService

def create_batch_for_ops(user_id, batch_payload):
    return {"id": str(uuid4()), "created_by": str(user_id), "payload": batch_payload}

def get_ops_performance(user_id):
    metrics = OpsPerformanceService.compute_metrics()
    metrics["user_id"] = str(user_id)
    return metrics


def get_ops_alerts(user_id):
    now = datetime.utcnow()
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
