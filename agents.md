# agents.md — Mami Supermarket (Backend)

This file defines the project agents (responsibilities), coding rules, workflows, and quality gates for the backend.

---

## 1) Project Context (Backend Only)

**Stack**
- Python, Flask (App Factory + Blueprints)
- PostgreSQL
- SQLAlchemy + Alembic
- JWT Auth (Flask-JWT-Extended)
- Pydantic Schemas (DTOs) for request/response contracts
- httpx/requests for payment provider
- pytest for tests
- ruff for lint/format

**Key Constraints**
- Inventory is real and **per branch**: (product_id, branch_id)
- Delivery orders deduct inventory from **The Warehouse**:
  - `DELIVERY_SOURCE_BRANCH_ID` in config
- Checkout requires **pessimistic locking** (`FOR UPDATE`)
- Audit is mandatory (old_value/new_value/context) and must be written **inside DB transactions**
- Product deletion is **soft delete** (`is_active=false`)
- Customer carts exist **only for registered customers** (no guest cart persistence)

---

## 2) Agents & Responsibilities

### A) API Agent (Routes & Contracts)
**Owns**
- Flask blueprints, route registration, endpoint naming
- Input parsing + Pydantic validation
- Response envelopes:
  - `{ "data": ... }`
  - `{ "error": { code, message, details } }`
  - Pagination envelope

**Must**
- Never implement business logic in routes
- Only call service layer
- Apply `require_auth`, `require_role`, and ownership checks where relevant

---

### B) Schema Agent (Pydantic DTOs)
**Owns**
- `app/schemas/` request & response models
- Consistent API shapes and backward compatibility

**Must**
- Separate DB Models vs API contracts
- Expose only safe fields (no password hash, no raw payment tokens, etc.)
- Provide stable response structures for frontend

---

### C) Domain Model Agent (SQLAlchemy Models)
**Owns**
- `app/models/` entities + enums
- Relationships + constraints + indexes
- Snapshot fields in orders

**Must**
- Enforce non-null required fields (per spec)
- Soft delete where needed (`is_active`)
- Use composite unique constraints for inventory: (product_id, branch_id)

---

### D) Service Agent (Business Logic)
**Owns**
- `app/services/`
- Implements business rules and transaction boundaries

**Must**
- Keep services cohesive (no “god services”)
- Checkout is orchestrator and may call:
  - InventoryService (locking/decrement)
  - PaymentService (tokenization charge)
  - OrderService (create order + snapshots)
  - AuditService (old/new within transaction)
- Use consistent domain exceptions mapped to error codes

---

### E) Inventory Agent (Locking & Stock Integrity)
**Owns**
- Inventory verification and decrement logic
- Lock strategy for checkout confirm

**Must**
- Use **pessimistic locking**:
  - `SELECT ... FOR UPDATE` / `with_for_update()`
- Verify availability before decrement
- Operate on **branch-specific inventory**
- Delivery always uses `DELIVERY_SOURCE_BRANCH_ID`

---

### F) Payments Agent (External Provider)
**Owns**
- Payment provider integration (tokenization)
- Error mapping and reference IDs

**Must**
- Charge only after inventory rows are locked
- Never store card details—only provider token/reference
- Provide safe metadata (order_number, user_id, request_id)

**Danger Zone Rule**
- If payment succeeds but DB commit fails:
  - log `PAYMENT_CAPTURED_NOT_COMMITTED` with reference for reconciliation

---

### G) Audit Agent (Compliance & Recovery)
**Owns**
- `Audit` records with old/new/context
- Guarantees audit writes only occur on successful transaction commits

**Must**
- Capture old_value before update
- Capture new_value after update
- Write audit inside the **same DB transaction**
- Provide filters/pagination for `/admin/audit`

---

### H) Ops Agent (Employee Workflows)
**Owns**
- Order picking, missing items, status changes, urgency sorting

**Must**
- Enforce role-based status transition rules:
  - Employee: CREATED→IN_PROGRESS, IN_PROGRESS→READY (only if all picked), IN_PROGRESS→MISSING (if any missing)
  - Manager/Admin: full transitions
- Marking missing + finishing sets order to `MISSING`

---

### I) Stock Requests Agent (Employee → Manager)
**Owns**
- StockRequest creation and approvals
- Bulk approvals (partial success)

**Must**
- Employee cannot edit inventory directly
- Manager/Admin approve/reject with audit old/new
- Bulk review returns per-item result; no all-or-nothing

---

## 3) Non-Negotiable Rules (Quality Gates)

### Transactions & Locking
- `POST /checkout/confirm` must run inside a DB transaction:
  - lock inventory rows with `FOR UPDATE`
  - verify quantities
  - charge payment
  - create order + order items
  - decrement inventory
  - audit
  - commit

### Consistent Error Contracts
All errors returned as:
```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
Ownership
	•	Customers may access only their resources
	•	Ownership mismatch should return 404 (recommended)

Pagination

Required for:
	•	GET /ops/orders
	•	GET /admin/audit
Recommended for:
	•	GET /orders, GET /products/search, stock request lists

Parameters:
	•	limit default 50, max 200
	•	offset default 0

Soft Delete
	•	Products/Categories/Branches are deactivated via is_active=false
	•	No physical deletes that can break order history

⸻

4) Endpoint Summary (Backend Scope)

Auth
	•	POST /api/v1/auth/register
	•	POST /api/v1/auth/login
	•	POST /api/v1/auth/change-password

Catalog
	•	GET /api/v1/categories
	•	GET /api/v1/categories/:id/products
	•	GET /api/v1/products/:id
	•	GET /api/v1/products/search
	•	GET /api/v1/products/autocomplete

Cart (customer only)
	•	GET /api/v1/cart
	•	POST/PUT/DELETE /api/v1/cart/items
	•	DELETE /api/v1/cart

Checkout
	•	POST /api/v1/checkout/preview
	•	POST /api/v1/checkout/confirm

Orders
	•	GET /api/v1/orders
	•	GET /api/v1/orders/:id
	•	POST /api/v1/orders/:id/cancel (CREATED only)

Ops
	•	GET /api/v1/ops/orders (pagination + urgency)
	•	GET /api/v1/ops/orders/:id
	•	PATCH /api/v1/ops/orders/:id/items/:itemId/picked-status
	•	PATCH /api/v1/ops/orders/:id/status

Stock Requests
	•	POST /api/v1/stock-requests
	•	GET /api/v1/stock-requests/my
	•	GET /api/v1/admin/stock-requests
	•	PATCH /api/v1/admin/stock-requests/:id/review
	•	PATCH /api/v1/admin/stock-requests/bulk-review

Audit
	•	GET /api/v1/admin/audit (pagination + filters)

⸻

5) Definition of Done (DoD)

A feature is DONE only if:
	•	DTO schemas exist (request/response)
	•	route calls service only (no business logic in route)
	•	RBAC and ownership applied
	•	audit added where required
	•	tests added for critical paths
	•	ruff passes
	•	alembic migration exists if DB changes occurred

⸻

6) Testing Priorities (Must Have)
	•	Checkout oversell prevention (locking works)
	•	Branch switch causes INSUFFICIENT_STOCK
	•	Employee status transition restrictions
	•	Ownership returns 404 for чужие resource
	•	Bulk stock request review returns partial success
	•	Audit is not written if transaction rolls back

⸻

7) Naming & Conventions
	•	Blueprints per domain (auth, catalog, cart, checkout, orders, ops, admin)
	•	Service methods are verbs: create_, update_, finalize_, lock_and_verify_
	•	Error codes are UPPER_SNAKE_CASE

⸻

8) Project Defaults
	•	DELIVERY_SOURCE_BRANCH_ID points to “The Warehouse” branch
	•	Delivery slots are 2 hours, 06:00–22:00
	•	Delivery min ₪150; under min fee ₪30