# TODO — Mami Supermarket (Backend → Client)

This TODO is organized as a practical execution plan.
- Backend first (Flask + PostgreSQL)
- Then Client (web app)
Each task is written as a checkbox so you can track progress in GitHub.

---

## Phase 0 — Repo & Tooling (Day 0)
- [x] Create repository structure:
  - [x] `app/` (routes, services, models, schemas, common)
  - [x] `migrations/`
  - [x] `tests/`
  - [x] `wsgi.py` / `run.py`
- [x] Add `README.md` (project overview + run instructions)
- [x] Add `.gitignore` (Python, venv, .env, node_modules if needed later)
- [x] Add `.env.example` with all required env vars
- [x] Add `agents.md` (project rules)
- [x] Add `TODO.md` (this file)
- [x] Add `ruff.toml` (or `pyproject.toml` for ruff)
- [x] Add `pytest.ini`
- [x] Add `pre-commit` config (optional but recommended)
- [x] Install deps:
  - [x] Flask
  - [x] SQLAlchemy
  - [x] Alembic
  - [x] psycopg2-binary (or psycopg)
  - [x] Flask-JWT-Extended
  - [x] passlib[bcrypt]
  - [x] pydantic
  - [x] httpx
  - [x] Flask-Cors
  - [x] Flask-Limiter
  - [x] pytest + pytest-cov
- [x] Implement Flask app factory:
  - [x] `create_app()`
- [x] register blueprints
- [x] init extensions (db, jwt, cors, limiter)
- [x] Implement standard response helpers:
  - [x] Success envelope: `{ "data": ... }`
  - [x] Error envelope: `{ "error": { code, message, details } }`
  - [x] Pagination envelope
- [x] Global error handlers:
  - [x] validation errors
  - [x] auth errors
  - [x] domain errors (business conflicts)
  - [x] internal errors with requestId logging
- [x] Add requestId middleware (correlation id) and structured logging

---

## Phase 1 — Database Foundation (Models + Migrations)
### 1.1 Enums
  - [x] Define enums:
  - [x] `Role`: CUSTOMER, EMPLOYEE, MANAGER, ADMIN
  - [x] `OrderStatus`: CREATED, IN_PROGRESS, READY, OUT_FOR_DELIVERY, DELIVERED, CANCELED, DELAYED, MISSING
  - [x] `FulfillmentType`: DELIVERY, PICKUP
  - [x] `PickedStatus`: PENDING, PICKED, MISSING
  - [x] `StockRequestType`: SET_QUANTITY, ADD_QUANTITY
  - [x] `StockRequestStatus`: PENDING, APPROVED, REJECTED
  - [x] `CartStatus`: ACTIVE, CHECKED_OUT, ABANDONED

### 1.2 Models (SQLAlchemy)
- [x] User (all fields required)
- [x] Address (all fields required)
- [x] PaymentToken (provider + token only; required fields)
- [x] Category (required)
- [x] Product (required + `is_active`)
- [x] Branch (required + `is_active`)
- [x] Inventory **per branch** (required, unique `(product_id, branch_id)`)
- [x] DeliverySlot (required)
- [x] Cart (customer only, required)
- [x] CartItem (required)
- [x] Order (required)
- [x] OrderDeliveryDetails (required for delivery)
- [x] OrderPickupDetails (required for pickup)
- [x] OrderItem (required + snapshots)
- [x] StockRequest (required + branch_id)
- [x] Audit (required old_value/new_value/context)

### 1.3 Constraints & Indexes
- [x] Unique: `users.email`
- [x] Unique: `products.sku`
- [x] Unique: `(inventory.product_id, inventory.branch_id)`
- [x] Indexes:
  - [x] products: name, sku, category_id
  - [x] orders: user_id, status, created_at
  - [x] stock_requests: status, branch_id, created_at
  - [x] audit: entity_type, entity_id, actor_user_id, created_at

### 1.4 Alembic
- [x] `alembic init`
- [x] Create first migration
- [ ] Apply migration to dev DB

### 1.5 Seed / Bootstrap
- [x] Create branches seed:
  - [x] "The Warehouse" branch (store its id)
- [x] Create delivery slots seed:
  - [x] 2-hour windows from 06:00 to 22:00 for each day_of_week
- [ ] Create admin user seed (optional for dev)

---

## Phase 2 — Schemas (Pydantic DTO Layer)
### 2.1 Common
- [ ] `ErrorResponse`
- [ ] `Pagination`
- [ ] `PaginatedResponse[T]`

### 2.2 Auth
- [ ] `RegisterRequest`, `LoginRequest`, `ChangePasswordRequest`
- [ ] `UserResponse`, `AuthResponse`

### 2.3 Catalog
- [ ] `CategoryResponse`
- [ ] `ProductResponse` (includes `in_stock_anywhere`, optional `in_stock_for_branch`)
- [ ] `ProductSearchResponse` (paginated)
- [ ] `AutocompleteResponse`

### 2.4 Cart
- [ ] `CartItemUpsertRequest`
- [ ] `CartItemResponse`
- [ ] `CartResponse`

### 2.5 Checkout
- [ ] `CheckoutPreviewRequest/Response`
- [ ] `CheckoutConfirmRequest/Response`

### 2.6 Orders
- [ ] `OrderItemResponse`
- [ ] `OrderResponse`
- [ ] `OrderListResponse` (paginated)
- [ ] `CancelOrderResponse`

### 2.7 Ops
- [ ] `OpsOrdersQuery`
- [ ] `OpsOrderResponse`
- [ ] `UpdatePickStatusRequest`
- [ ] `UpdateOrderStatusRequest`

### 2.8 Stock Requests
- [ ] `StockRequestCreateRequest`
- [ ] `StockRequestReviewRequest`
- [ ] `BulkReviewRequest`
- [ ] `StockRequestResponse`

### 2.9 Audit
- [ ] `AuditQuery`
- [ ] `AuditResponse`

---

## Phase 3 — Auth + RBAC + Ownership
- [ ] Implement password hashing utilities (passlib)
- [ ] JWT setup (Flask-JWT-Extended):
  - [ ] token includes user_id + role
- [ ] Middleware:
  - [ ] `require_auth`
  - [ ] `require_role(roles[])`
  - [ ] `require_ownership(resource_loader)` with MANAGER/ADMIN bypass
  - [ ] Ownership mismatch returns 404
- [ ] Auth routes:
  - [ ] `POST /api/v1/auth/register` (CUSTOMER only)
  - [ ] `POST /api/v1/auth/login` (all roles)
  - [ ] `POST /api/v1/auth/change-password`
- [ ] Rate limit login endpoint (Flask-Limiter)
- [ ] Audit login success/fail (optional but recommended)

---

## Phase 4 — Catalog (Public Read + Admin Manage)
### 4.1 Public endpoints
- [ ] `GET /api/v1/categories`
- [ ] `GET /api/v1/categories/:id/products?branchId=...`
- [ ] `GET /api/v1/products/:id?branchId=...`
- [ ] `GET /api/v1/products/search?q=...&categoryId=...&inStock=true&branchId=...&limit=&offset=`
- [ ] `GET /api/v1/products/autocomplete?q=...&limit=10`

### 4.2 Admin endpoints (MANAGER/ADMIN)
- [ ] Categories:
  - [ ] create/update/deactivate (soft delete)
- [ ] Products:
  - [ ] create/update/deactivate (soft delete)
- [ ] Audit for each create/update/deactivate

---

## Phase 5 — Branches, DeliverySlots, Inventory (Admin)
- [ ] `GET /api/v1/branches`
- [ ] `GET /api/v1/delivery-slots?dayOfWeek=...`

Admin (MANAGER/ADMIN):
- [ ] Branch CRUD + deactivate
- [ ] DeliverySlot CRUD + deactivate
- [ ] Inventory endpoints:
  - [ ] `GET /api/v1/admin/inventory?branchId=&productId=&limit=&offset=`
  - [ ] `PUT /api/v1/admin/inventory/:id` (update quantity)
- [ ] Audit inventory updates (old/new)
- [ ] Ensure DELIVERY_SOURCE_BRANCH_ID exists in DB

---

## Phase 6 — Cart (Customer Only)
- [ ] `GET /api/v1/cart`
- [ ] `POST /api/v1/cart/items`
- [ ] `PUT /api/v1/cart/items/:id`
- [ ] `DELETE /api/v1/cart/items/:id`
- [ ] `DELETE /api/v1/cart` (clear)
- [ ] Validations:
  - [ ] product is_active
  - [ ] quantity >= 1
  - [ ] block if `OUT_OF_STOCK_ANYWHERE` (no stock in any branch)
- [ ] Audit cart actions (optional but recommended)

---

## Phase 7 — Checkout (Critical Path)
### 7.1 Checkout Preview
- [ ] `POST /api/v1/checkout/preview`
- [ ] Resolve branch:
  - [ ] DELIVERY → `DELIVERY_SOURCE_BRANCH_ID`
  - [ ] PICKUP → selected branch
- [ ] Validate delivery slot: 2-hour window between 06:00–22:00
- [ ] Revalidate inventory against resolved branch
- [ ] Compute totals:
  - [ ] delivery fee rules (min ₪150, else ₪30 or suggest pickup)
- [ ] Return missing items details if insufficient stock

### 7.2 Checkout Confirm (Transactional + Locking)
- [ ] `POST /api/v1/checkout/confirm`
- [ ] Implement **pessimistic locking**:
  - [ ] `db.session.begin()`
  - [ ] `InventoryService.lock_and_verify(...).with_for_update()`
  - [ ] verify quantities
- [ ] Payment integration (Tokenization):
  - [ ] charge only after lock, before commit
  - [ ] map provider errors to `PAYMENT_FAILED`
- [ ] Create order:
  - [ ] order_number generation
  - [ ] create Order + DeliveryDetails/PickupDetails
  - [ ] create OrderItems snapshots
- [ ] Decrement inventory (locked rows)
- [ ] Audit inside transaction:
  - [ ] order created
  - [ ] inventory decremented (old/new)
  - [ ] status initial
- [ ] Commit
- [ ] Payment “danger zone” mitigation:
  - [ ] log `PAYMENT_CAPTURED_NOT_COMMITTED` if commit fails after payment success

### 7.3 Save Default Payment Token
- [ ] If `save_as_default=true`:
  - [ ] upsert PaymentToken and mark as default (unset previous default)
  - [ ] audit token save event (no raw token logging)

### 7.4 Idempotency (Recommended)
- [ ] Add `Idempotency-Key` header support for checkout confirm
- [ ] Create `idempotency_keys` table
- [ ] Return saved response for same key+hash, else conflict error

---

## Phase 8 — Orders (Customer)
- [ ] `GET /api/v1/orders?limit=&offset=`
- [ ] `GET /api/v1/orders/:id` (ownership)
- [ ] `POST /api/v1/orders/:id/cancel` (ownership)
- [ ] Cancel rules:
  - [ ] only if status=CREATED
  - [ ] audit cancellation
  - [ ] (optional) refund workflow if needed by provider

---

## Phase 9 — Ops (Employee/Manager/Admin)
### 9.1 Orders List (Ops)
- [ ] `GET /api/v1/ops/orders?...&limit=&offset=`
- [ ] Filters:
  - [ ] status
  - [ ] dateFrom/dateTo
  - [ ] urgency sorting by delivery slot start time

### 9.2 Order Details (Ops)
- [ ] `GET /api/v1/ops/orders/:id`

### 9.3 Picking
- [ ] `PATCH /api/v1/ops/orders/:id/items/:itemId/picked-status`
- [ ] Audit item picked_status changes

### 9.4 Status Updates
- [ ] `PATCH /api/v1/ops/orders/:id/status`
- [ ] Enforce transitions:
  - [ ] Employee limited transitions
  - [ ] READY only if all items PICKED and none missing
  - [ ] MISSING if any item missing and employee finishes
- [ ] Audit status changes with old/new

---

## Phase 10 — Stock Requests (Employee → Manager/Admin)
### 10.1 Employee
- [ ] `POST /api/v1/stock-requests` (must include branch_id)
- [ ] `GET /api/v1/stock-requests/my?limit=&offset=`

### 10.2 Manager/Admin Review
- [ ] `GET /api/v1/admin/stock-requests?status=PENDING&limit=&offset=`
- [ ] `PATCH /api/v1/admin/stock-requests/:id/review`
  - [ ] APPROVED updates inventory (SET or ADD) + audit old/new
  - [ ] REJECTED sets status + audit
- [ ] Bulk review:
  - [ ] `PATCH /api/v1/admin/stock-requests/bulk-review`
  - [ ] Partial success response per ID
  - [ ] Audit each request separately

---

## Phase 11 — Audit Viewer (Manager/Admin)
- [ ] `GET /api/v1/admin/audit?...&limit=&offset=`
- [ ] Filters:
  - [ ] entity_type
  - [ ] action
  - [ ] actor
  - [ ] date range
- [ ] Ensure pagination and indexes support large datasets

---

## Phase 12 — Testing (Must-Have)
- [ ] Checkout oversell prevention:
  - [ ] concurrent requests cannot oversell last unit
- [ ] Branch switching:
  - [ ] preview returns INSUFFICIENT_STOCK for pickup branch change
- [ ] Ownership:
  - [ ] customer gets 404 when accessing another user’s order
- [ ] Employee transitions:
  - [ ] invalid status transition returns 409 INVALID_STATUS_TRANSITION
- [ ] Missing items flow:
  - [ ] marking missing then finishing sets order status to MISSING
- [ ] Bulk review:
  - [ ] returns partial success and does not fail entire batch
- [ ] Audit transactional integrity:
  - [ ] if service rolls back, no audit row exists
- [ ] Payment danger zone simulation (at least log path)

---

## Phase 13 — Release Readiness
- [ ] Add production run scripts (gunicorn)
- [ ] Add DB migration run instructions
- [ ] Add seed script instructions (warehouse + delivery slots)
- [ ] Add health endpoint:
  - [ ] `GET /api/v1/health` (DB connectivity optional)
- [ ] Verify ruff + tests pass in CI (optional but recommended)

---

## Phase 14 — Client Prep (After Backend MVP)
- [ ] Publish OpenAPI-like docs (manual) or postman collection
- [ ] Provide sample JSON for top endpoints (auth/cart/checkout/ops/stock)
- [ ] Define frontend error handling rules based on ErrorResponse
