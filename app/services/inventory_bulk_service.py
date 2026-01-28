import csv
from flask import request ,jsonify

from app.extensions import db
from app.models.inventory import Inventory
from app.utils.responses import error_envelope, success_envelope


def handle_bulk_inventory_upload():
    file = request.files.get("file")
    if not file:
        return (
            jsonify(
                error_envelope(
                    "NO_FILE",
                    "Please attach a CSV file before uploading inventory.",
                    status_code=400,
                ),
            ),
            400,
        )
    reader = csv.DictReader(file.stream.read().decode("utf-8").splitlines())
    processed = []
    success_count = 0
    error_count = 0
    errors = []
    for idx, row in enumerate(reader, 1):
        try:
            product_id = int(row["product_id"])
            branch_id = int(row["branch_id"])
            available_quantity = int(row.get("available_quantity", 0))
            reserved_quantity = int(row.get("reserved_quantity", 0))
        except Exception as e:
            error_count += 1
            errors.append({"row_number": idx, "row": row, "error": str(e)})
            processed.append({"row_number": idx, "status": "error", "error": str(e), "row": row})
            continue

        inv = db.session.query(Inventory).filter_by(product_id=product_id, branch_id=branch_id).first()
        if inv:
            inv.available_quantity = available_quantity
            inv.reserved_quantity = reserved_quantity
            action = "updated"
        else:
            inv = Inventory(
                product_id=product_id,
                branch_id=branch_id,
                available_quantity=available_quantity,
                reserved_quantity=reserved_quantity,
            )
            db.session.add(inv)
            action = "created"
        success_count += 1
        processed.append({"row_number": idx, "product_id": str(product_id), "branch_id": str(branch_id), "status": "success", "action": action})

    db.session.commit()
    summary = {
        "total": len(processed),
        "success": success_count,
        "errors": error_count,
        "error_details": errors,
        "results": processed
    }
    return jsonify(success_envelope(summary)), 202
