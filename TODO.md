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
- [x] Apply migration to dev DB

### 1.5 Seed / Bootstrap
- [x] Create branches seed:
  - [x] "The Warehouse" branch (store its id)
- [x] Create delivery slots seed:
  - [x] 2-hour windows from 06:00 to 22:00 for each day_of_week
- [x] Create admin user seed (optional for dev)

---

## Phase 2 — Schemas (Pydantic DTO Layer)
### 2.1 Common
- [x] `ErrorResponse`
- [x] `Pagination`
- [x] `PaginatedResponse[T]`

### 2.2 Auth
- [x] `RegisterRequest`, `LoginRequest`, `ChangePasswordRequest`
- [x] `UserResponse`, `AuthResponse`

### 2.3 Catalog
- [x] `CategoryResponse`
- [x] `ProductResponse` (includes `in_stock_anywhere`, optional `in_stock_for_branch`)
- [x] `ProductSearchResponse` (paginated)
- [x] `AutocompleteResponse`

### 2.4 Cart
- [x] `CartItemUpsertRequest`
- [x] `CartItemResponse`
- [x] `CartResponse`

### 2.5 Checkout
- [x] `CheckoutPreviewRequest/Response`
- [x] `CheckoutConfirmRequest/Response`

### 2.6 Orders
- [x] `OrderItemResponse`
- [x] `OrderResponse`
- [x] `OrderListResponse` (paginated)
- [x] `CancelOrderResponse`

### 2.7 Ops
- [x] `OpsOrdersQuery`
- [x] `OpsOrderResponse`
- [x] `UpdatePickStatusRequest`
- [x] `UpdateOrderStatusRequest`

### 2.8 Stock Requests
- [x] `StockRequestCreateRequest`
- [x] `StockRequestReviewRequest`
- [x] `BulkReviewRequest`
- [x] `StockRequestResponse`

### 2.9 Audit
- [x] `AuditQuery`
- [x] `AuditResponse`

## Phase 3 — Auth + RBAC + Ownership
- [x] Implement password hashing utilities (passlib)
- [x] JWT setup (`Flask-JWT-Extended`)
  - [x] token includes user_id + role
- [x] Middleware:
  - [x] `require_auth`
  - [x] `require_role(roles[])`
  - [x] `require_ownership(resource_loader)` w/ admin bypass + ownership 404
- [x] Auth routes:
  - [x] `POST /api/v1/auth/register`
  - [x] `POST /api/v1/auth/login`
  - [x] `POST /api/v1/auth/change-password`
- [x] Rate limit login endpoint
- [x] Audit login success/fail (optional)

---

## Phase 4 — Catalog (Public Read + Admin Manage)
### 4.1 Public endpoints
- [x] `GET /api/v1/categories`
- [x] `GET /api/v1/categories/:id/products?branchId=...`
- [x] `GET /api/v1/products/:id?branchId=...`
- [x] `GET /api/v1/products/search?q=...&categoryId=...&inStock=true&branchId=...&limit=&offset=`
- [x] `GET /api/v1/products/autocomplete?q=...&limit=10`

### 4.2 Admin endpoints (MANAGER/ADMIN)
- [x] Categories:
  - [x] create/update/deactivate (soft delete)
- [x] Products:
  - [x] create/update/deactivate (soft delete)
- [x] Audit for each create/update/deactivate

---

## Phase 5 — Branches, DeliverySlots, Inventory (Admin)
- [x] `GET /api/v1/branches`
- [x] `GET /api/v1/delivery-slots?dayOfWeek=...`

Admin (MANAGER/ADMIN):
- [x] Branch CRUD + deactivate
- [x] DeliverySlot CRUD + deactivate
- [x] Inventory endpoints:
  - [x] `GET /api/v1/admin/inventory?branchId=&productId=&limit=&offset=`
  - [x] `PUT /api/v1/admin/inventory/:id` (update quantity)
- [x] Audit inventory updates (old/new)
- [x] Ensure DELIVERY_SOURCE_BRANCH_ID exists in DB

---

## Phase 6 — Cart (Customer Only)
- [x] `GET /api/v1/cart`
- [x] `POST /api/v1/cart/items`
- [x] `PUT /api/v1/cart/items/:id`
- [x] `DELETE /api/v1/cart/items/:id`
- [x] `DELETE /api/v1/cart` (clear)
- [x] Validations:
  - [x] product is_active
  - [x] quantity >= 1
  - [x] block if `OUT_OF_STOCK_ANYWHERE` (no stock in any branch)
- [x] Audit cart actions

---

## Phase 7 — Checkout (Critical Path)
### 7.1 Checkout Preview
- [x] `POST /api/v1/checkout/preview`
- [x] Resolve branch:
  - [x] DELIVERY → `DELIVERY_SOURCE_BRANCH_ID`
  - [x] PICKUP → selected branch
- [x] Validate delivery slot: 2-hour window between 06:00–22:00
- [x] Revalidate inventory against resolved branch
- [x] Compute totals:
  - [x] delivery fee rules (min ₪150, else ₪30)
- [x] Return missing items details if insufficient stock

### 7.2 Checkout Confirm (Transactional + Locking)
- [x] `POST /api/v1/checkout/confirm`
- [x] Implement **pessimistic locking**:
  - [x] `db.session.begin()`/`with_for_update()`
  - [x] verify quantities
- [x] Payment integration (stubbed):
  - [x] charge only after lock, before commit
- [x] Create order:
  - [x] order_number generation
  - [x] create Order + DeliveryDetails/PickupDetails
  - [x] create OrderItems snapshots
- [x] Decrement inventory (locked rows)
- [x] Audit inside transaction:
  - [x] order created
  - [x] inventory decremented (old/new)
- [x] Commit
- [x] Payment “danger zone” mitigation (not yet)

### 7.3 Save Default Payment Token
- [x] If `save_as_default=true`:
  - [x] upsert PaymentToken and mark as default (unset previous default)
  - [x] audit token save event (no raw token logging)

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
