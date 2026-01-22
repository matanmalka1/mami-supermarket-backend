from uuid import uuid4
from app.models.enums import Role
from app.utils.responses import success_envelope

def create_batch_for_ops(user_id, batch_payload):
    # TODO: implement real batch creation logic
    return {"id": str(uuid4()), "created_by": str(user_id), "payload": batch_payload}

def get_ops_performance(user_id):
    # TODO: implement real performance logic
    return {"score": 100, "user_id": str(user_id)}

def get_ops_map(user_id):
    # TODO: implement real map logic
    return {
        "map": {
            "branches": [
                {"id": "branch-1", "name": "Main Branch", "lat": 32.1, "lng": 34.8},
                {"id": "branch-2", "name": "North Branch", "lat": 32.2, "lng": 34.9}
            ],
            "warehouse": {"id": "warehouse-1", "name": "Central Warehouse", "lat": 32.15, "lng": 34.85}
        },
        "user_id": str(user_id)
    }
