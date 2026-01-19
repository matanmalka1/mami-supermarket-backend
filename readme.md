# Mami Supermarket Backend

**Flask + PostgreSQL · Real Inventory · Multi-Branch · Tokenized Payments · Audit Trail**

```text
| \/ | (_) | |
| \ / | \_\_ _ _ \_\_ _ | |
| |\/| |/ _` | '_ ` _ \ |
| | | | (_| | | | | | |
|_| |_|\__,_|_| |_| |\_|
          Supermarket · Online Ordering System
```

## Table of Contents

1. [Overview](#overview)
2. [Key Business Rules](#key-business-rules)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Main Features](#main-features)
6. [Roles & Permissions](#roles--permissions)
7. [Important Concepts](#important-concepts)
8. [Getting Started](#getting-started)
9. [Environment Variables](#environment-variables)
10. [Database Models Overview](#database-models-overview)
11. [Important Endpoints Groups](#important-endpoints-groups)
12. [Checkout Flow – Critical Path](#checkout-flow--critical-path)
13. [Audit & Security Philosophy](#audit--security-philosophy)
14. [Development Guidelines & Conventions](#development-guidelines--conventions)
15. [Production Recommendations](#production-recommendations)
16. [API Samples](docs/api.md)

## Overview

Backend API for **Mami Supermarket** – modern online supermarket system supporting:

- Real per-branch inventory (including central warehouse)
- Customer web shopping + cart
- Delivery (weekly days + 2-hour windows) & branch pickup
- Credit card tokenization payments
- Employee picking workflow + missing items handling
- Employee → Manager inventory update requests & approvals
- Strong audit trail with old/new values (transaction-safe)
- Role-based access control (RBAC) with ownership checks

## Key Business Rules (2026 edition)

- Cart exists only for registered customers
- Inventory is real and per-branch (including warehouse)
- Delivery always deducts from warehouse branch (configurable ID)
- Delivery minimum ₪150 → free delivery / ₪30 fee under minimum
- Payment → credit card tokenization only
- Soft-delete everywhere (is_active flag)
- Pessimistic locking during checkout confirmation
- Mandatory audit logging with old/new JSON values in same transaction

## Tech Stack

| Layer             | Technology                            |
| ----------------- | ------------------------------------- |
| Language          | Python 3.11+                          |
| Web Framework     | Flask                                 |
| ORM               | SQLAlchemy 2.x                        |
| Migrations        | Alembic                               |
| Validation        | Pydantic v2                           |
| Authentication    | JWT (Flask-JWT-Extended)              |
| Async HTTP        | httpx (payment provider calls)        |
| Database          | PostgreSQL 15+                        |
| Production Server | Gunicorn + Uvicorn workers (optional) |

## Project Structure (recommended)

```text
mami-backend/
├── alembic/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py           # db, jwt, etc.
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic DTOs (req/res)
│   ├── services/               # business logic
│   │   ├── checkout.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── audit.py
│   │   └── ...
│   ├── repositories/           # (optional) db access abstraction
│   ├── routes/                 # Flask Blueprints
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── customer.py
│   │   │   ├── catalog.py
│   │   │   ├── ops.py
│   │   │   ├── admin.py
│   │   │   └── ...
│   ├── middleware/
│   │   ├── auth.py
│   │   ├── ownership.py
│   │   └── error_handler.py
│   ├── utils/
│   └── constants.py
├── tests/
├── migrations/
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md          ← You are here
```

## Main Features

- Customer registration & profile management
- Multi-branch catalog with real-time stock visibility
- Cart (one active per user)
- Two fulfillment types: Delivery / Pickup
- Pessimistic locking + double-check during checkout
- Tokenized credit-card payments (no card data stored)
- Order fulfillment workflow (picking → missing → ready/missing)
- Employee inventory update requests → manager approval
- Full audit trail (who changed what, before & after)

## Roles & Permissions (Quick Summary)

| Action                             | Customer | Employee | Manager | Admin |
| ---------------------------------- | :------: | :------: | :-----: | :---: |
| Browse catalog                     |    ✓     |    ✓     |    ✓    |   ✓   |
| Manage own cart & checkout         |    ✓     |          |         |       |
| View / cancel own orders (CREATED) |    ✓     |          |    ✓    |   ✓   |
| View all orders + picking          |          |    ✓     |    ✓    |   ✓   |
| Change order status (limited)      |          |    ✓     |  full   | full  |
| Direct inventory change            |          |          |    ✓    |   ✓   |
| Create stock update request        |          |    ✓     |    ✓    |   ✓   |
| Approve/reject stock requests      |          |          |    ✓    |   ✓   |
| Bulk review stock requests         |          |          |    ✓    |   ✓   |
| View audit logs                    |          |          |    ✓    |   ✓   |

## Important Concepts

1. **Warehouse branch** – special branch used for all deliveries
2. **Pessimistic locking** – SELECT ... FOR UPDATE during checkout confirmation
3. **Danger Zone** – payment succeeded but DB commit failed → needs reconciliation
4. **Audit must be transactional** – same transaction as the change or nothing
5. **Soft delete only** – is_active flag everywhere
6. **Ownership middleware** – customers see only their resources (404 on mismatch)
7. **Stock requests** – employees cannot change inventory directly

## Getting Started

```bash
# 1. Clone & enter
git clone ...
cd mami-backend

# 2. Create & activate virtualenv
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy example env
cp .env.example .env

# 5. Edit .env !! important !!
# especially:
# DATABASE_URL
# JWT_SECRET_KEY
# DELIVERY_SOURCE_BRANCH_ID

# 6. Initialize DB & run migrations
./venv/bin/alembic upgrade head

# 7. Seed warehouse + delivery slots (dev)
./venv/bin/python scripts/seed.py

# 8. Run development server
./venv/bin/python run.py
# or for production (Gunicorn)
./scripts/gunicorn.sh
```

## Environment Variables (.env)

```bash
# Required
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/mami

JWT_SECRET_KEY=super-long-random-secret-at-least-64-chars

# Warehouse branch (must exist in DB!)
DELIVERY_SOURCE_BRANCH_ID=uuid-or-int-of-warehouse

# Money rules
DELIVERY_MIN_TOTAL=150
DELIVERY_FEE_UNDER_MIN=30

# Delivery time windows
DELIVERY_START_TIME=06:00
DELIVERY_END_TIME=22:00
DELIVERY_SLOT_HOURS=2

# Pagination defaults
DEFAULT_LIMIT=50
MAX_LIMIT=200

# Optional / recommended
PAYMENT_PROVIDER_API_KEY=...
PAYMENT_PROVIDER_URL=https://...
LOG_LEVEL=INFO
```

## Database Models Overview (main ones)

```text
User → Address → PaymentToken
          ↓
       Category → Product ← Inventory (per branch)
                           ↓
                        Cart → CartItem
                           ↓
                        Order → OrderItem (snapshots!)
                           ↳ OrderDeliveryDetails / OrderPickupDetails
                           ↳ Audit (old/new JSON)
```

Also:
Branch, DeliverySlot, StockRequest

## Important Endpoints Groups

| Group                  | Base Path                      | Who can use   |
|------------------------|--------------------------------|---------------|
| Auth                   | /api/v1/auth                   | Public        |
| Profile                | /api/v1/me                     | Authenticated |
| Catalog                | /api/v1/categories, /products  | Everyone      |
| Cart                   | /api/v1/cart                   | Customer      |
| Checkout               | /api/v1/checkout               | Customer      |
| Customer Orders        | /api/v1/orders                 | Customer      |
| Operations (picking)   | /api/v1/ops/orders             | Employee+     |
| Stock Requests         | /api/v1/stock-requests         | Employee+     |
| Admin Stock Requests   | /api/v1/admin/stock-requests   | Manager+      |
| Admin Audit            | /api/v1/admin/audit            | Manager+      |

## Checkout Flow – Critical Path

The checkout process is the most critical and sensitive part of the system. It is designed as a multi-stage flow to ensure data consistency and financial safety.

**Preview**: Performs an optimistic stock check and calculates totals, taxes, and fees for the user to review.

**Confirm**: A strictly orchestrated transactional process:

1. **BEGIN TRANSACTION**
2. **Pessimistic Locking**: SELECT inventory FOR UPDATE
3. **Payment**: Charge token via external provider
4. **Success Path**:
   - Create Order + snapshots
   - Decrement inventory
   - Write Audit entries
   - COMMIT → 201 Order created
5. **Failure Paths**:
   - Stock insufficient → ROLLBACK → 409 INSUFFICIENT_STOCK
   - Payment failed → ROLLBACK → 400 PAYMENT_FAILED

**Idempotency-Key**: This header is mandatory for confirmation requests to prevent double-charging.

## Audit & Security Philosophy

- **Never trust frontend** – always re-validate stock, price, permissions
- **Audit is sacred** – must be in same transaction as change
- **404 for ownership violation** – better security than 403
- **Idempotency-Key** highly recommended for /confirm
- **Danger-zone logging** – payment captured but commit failed
