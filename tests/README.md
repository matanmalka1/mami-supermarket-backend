# Tests Directory Structure

This directory contains all backend API tests organized by domain.

## Structure

```
tests/
├── conftest.py                 # Shared fixtures (test_app, session, auth_header, etc.)
│
├── auth/                       # Authentication & Authorization
│   └── test_auth.py           # register, login, change password
│
├── profile/                    # User Profile Management
│   ├── profile_fixtures.py    # Profile-specific fixtures
│   ├── test_profile_update.py # Phone & profile updates
│   ├── test_profile_address_location.py # Address geolocation
│   ├── test_profile_addresses_list.py    # List & create addresses
│   ├── test_profile_addresses_update.py  # Update address
│   ├── test_profile_addresses_delete.py  # Delete address
│   └── test_profile_addresses_default.py # Set default address
│
├── cart/                       # Shopping Cart
│   └── test_cart.py           # Cart CRUD operations, out of stock
│
├── catalog/                    # Product Catalog
│   ├── test_catalog.py        # Categories, products, search
│   ├── test_catalog_contract.py # API contract, fields
│   ├── test_optional_fields_null.py # Optional fields
│   └── test_product_reviews.py # Product reviews
│
├── checkout/                   # Checkout Flow
│   └── test_checkout.py       # Preview, confirm, validation
│
├── orders/                     # Order Management
│   └── test_orders.py         # List orders, view details, cancel, ownership
│
├── ops/                        # Operations (Employee workflows)
│   ├── test_ops.py            # Order picking, status changes
│   └── test_ops_actions.py    # Lightweight ops endpoints
│
├── stock_requests/             # Stock Request Management
│   └── test_stock_requests.py # Create, review, bulk operations
│
├── branches/                   # Public Branch Endpoints
│   └── test_branches.py       # List branches, delivery slots
│
├── admin/                      # Admin Management
│   ├── test_admin_catalog.py  # Category & product CRUD
│   ├── test_admin_branches.py # Branch & inventory management
│   ├── test_admin_branches_security.py # Branch security
│   ├── test_admin_audit.py    # Audit log retrieval
│   ├── test_admin_settings.py # Settings endpoints
│   ├── test_admin_users.py    # User management
│   └── test_inventory_bulk.py # Bulk inventory upload
│
└── infrastructure/             # Cross-cutting concerns
    ├── test_audit_payment.py  # Audit & payment integration
    ├── test_branch_inventory.py # Branch inventory validation
    ├── test_rate_limit.py     # Rate limiting
    └── test_security_routes.py # RBAC & security
└── store/                      # Storefront endpoints
    └── test_store_endpoints.py # Storefront API smoke tests

```

## Running Tests

### All tests

```bash
pytest
```

### Specific domain

```bash
pytest tests/auth/
pytest tests/checkout/
pytest tests/admin/
```

### Specific file

```bash
pytest tests/auth/test_auth.py
```

### With coverage

```bash
pytest --cov=app --cov-report=html
```

## Test Coverage (by domain)

- **Auth**: register, login, password change
- **Profile**: phone, profile, addresses CRUD, geolocation
- **Cart**: operations, out of stock
- **Catalog**: toggle, search filters, contract, optional fields, reviews
- **Checkout**: oversell, payment, idempotency, fees
- **Orders**: ownership validation
- **Ops**: employee transitions, missing items, ops actions
- **Stock Requests**: bulk review, audit
- **Branches**: list, slots, filters
- **Admin**: catalog, branches, inventory, audit, security, settings, users, bulk upload
- **Infrastructure**: audit, rate limiting, RBAC, inventory
- **Store**: storefront endpoints

**Total: 80+ tests**
