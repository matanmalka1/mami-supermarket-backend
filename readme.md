# Mami Supermarket - Backend API

A production-grade RESTful API backend for an e-commerce supermarket platform, supporting customer-facing shopping experiences and internal operational workflows.

## Project Overview

The Mami Supermarket backend is a Flask-based API server that powers a full-featured online grocery delivery platform. It handles:

- **Customer Operations**: User registration, authentication, product browsing, cart management, checkout, and order tracking
- **Employee Operations**: Order picking, inventory management, and stock requests
- **Manager Operations**: Analytics, delivery slot management, catalog administration
- **Admin Operations**: User management, branch management, global settings, and audit trails

### Supported User Roles

The system implements four distinct user roles with hierarchical permissions:

- **CUSTOMER**: Browse products, manage cart, place orders, track deliveries
- **EMPLOYEE**: Process orders, update inventory, submit stock requests
- **MANAGER**: All employee permissions plus catalog management, delivery slots, analytics
- **ADMIN**: Full system access including user management, branch configuration, audit logs

### Core Responsibilities

- Secure JWT-based authentication with role-based authorization
- Product catalog with category hierarchies, search, and filtering
- Real-time cart management with inventory validation
- Multi-stage checkout with delivery slot selection and address management
- Order lifecycle management (created → picked → delivered)
- Idempotent payment operations
- Audit logging for compliance and debugging
- Rate limiting and security middleware

## Tech Stack

| Component            | Technology                                           |
| -------------------- | ---------------------------------------------------- |
| **Language**         | Python 3.11+                                         |
| **Framework**        | Flask 3.1+                                           |
| **Database**         | PostgreSQL (via SQLAlchemy 2.0)                      |
| **ORM**              | SQLAlchemy with declarative models                   |
| **Migrations**       | Alembic                                              |
| **Authentication**   | JWT (Flask-JWT-Extended)                             |
| **Validation**       | Pydantic 2.x for request/response schemas            |
| **Password Hashing** | Passlib with bcrypt                                  |
| **Email Service**    | Brevo (formerly Sendinblue) for transactional emails |
| **Rate Limiting**    | Flask-Limiter                                        |
| **Testing**          | pytest with coverage reporting                       |
| **Environment**      | python-dotenv for configuration                      |
| **WSGI Server**      | Gunicorn (production)                                |

## Architecture Overview

### Folder Structure

```
mami-supermarket-backend/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── config.py                # Environment-based configuration
│   ├── extensions.py            # Flask extension initialization (db, jwt, limiter)
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── base.py             # Base model, TimestampMixin, SoftDeleteMixin
│   │   ├── enums.py            # Shared enums (Role, OrderStatus, etc.)
│   │   ├── user.py             # User model
│   │   ├── product.py          # Product model
│   │   ├── cart.py             # Cart and CartItem models
│   │   ├── order.py            # Order and OrderItem models
│   │   └── ...                 # Additional domain models
│   │
│   ├── schemas/                 # Pydantic schemas for validation
│   │   ├── auth.py             # LoginRequest, RegisterRequest, AuthResponse
│   │   ├── cart.py             # CartItemUpsertRequest, CartResponse
│   │   ├── checkout.py         # CheckoutPreviewRequest, CheckoutConfirmRequest
│   │   └── ...                 # Additional request/response schemas
│   │
│   ├── routes/                  # Flask blueprints (API endpoints)
│   │   ├── auth_routes.py      # /api/v1/auth (register, login, password reset)
│   │   ├── cart_routes.py      # /api/v1/cart (cart CRUD)
│   │   ├── catalog_routes.py   # /api/v1/catalog (products, categories, search)
│   │   ├── checkout_routes.py  # /api/v1/checkout (preview, confirm)
│   │   ├── orders_routes.py    # /api/v1/orders (list, view, cancel)
│   │   ├── ops_routes.py       # /api/v1/ops (picking, inventory)
│   │   ├── admin_routes/       # /api/v1/admin/* (admin-only endpoints)
│   │   └── ...
│   │
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py     # User registration, authentication, password changes
│   │   ├── cart_service.py     # Cart operations
│   │   ├── checkout_service.py # Checkout preview/confirm, idempotency
│   │   ├── order_service.py    # Order creation, status updates
│   │   ├── email_service.py    # Brevo integration for emails
│   │   └── ...
│   │
│   ├── middleware/              # Request/response middleware
│   │   ├── auth.py             # require_auth, require_role decorators
│   │   ├── cors.py             # CORS configuration
│   │   ├── error_handler.py    # DomainError exception, global error handlers
│   │   ├── request_id.py       # Request ID injection
│   │   ├── request_logger.py   # Structured logging
│   │   ├── security_headers.py # Security headers (CSP, HSTS, etc.)
│   │   └── db_session.py       # Database session management
│   │
│   └── utils/                   # Shared utilities
│       ├── responses.py         # success_envelope, error_envelope, pagination_envelope
│       ├── security.py          # hash_password, verify_password
│       ├── logging_config.py    # Structured JSON logging
│       └── request_utils.py     # parse_json_or_400, current_user_id
│
├── alembic/                     # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic environment configuration
│
├── tests/                       # pytest test suite
│   ├── conftest.py             # Shared fixtures (test_app, session, auth_header)
│   ├── auth/                   # Authentication tests
│   ├── cart/                   # Cart tests
│   ├── checkout/               # Checkout tests
│   ├── admin/                  # Admin endpoint tests
│   └── ...
│
├── scripts/                     # Utility scripts
│   ├── gunicorn.sh             # Gunicorn startup script
│   └── seed/                   # Database seeding scripts
│
├── run.py                       # Development server entry point
├── wsgi.py                      # Production WSGI entry point
├── pyproject.toml               # Ruff linter configuration
├── requirements.txt             # Python dependencies
├── alembic.ini                 # Alembic configuration
└── .env                        # Environment variables (not in git)
```

### Separation of Concerns

The backend follows a layered architecture:

1. **Routes Layer** (`app/routes/`): Thin endpoints that handle HTTP concerns (parsing requests, returning responses). Decorated with `@jwt_required()` or role guards as needed.

2. **Services Layer** (`app/services/`): Contains all business logic. Services are stateless and accept validated Pydantic schemas as input. They orchestrate database operations and enforce business rules.

3. **Models Layer** (`app/models/`): SQLAlchemy ORM models representing database tables. Models include relationships, constraints, and basic model-level validation.

4. **Schemas Layer** (`app/schemas/`): Pydantic models for request validation and response serialization. Schemas enforce data contracts and type safety.

5. **Middleware Layer** (`app/middleware/`): Cross-cutting concerns like authentication, authorization, error handling, logging, and CORS.

6. **Utils Layer** (`app/utils/`): Reusable helper functions for responses, security, logging, and request parsing.

### Error Handling Strategy

The API uses a custom `DomainError` exception class for controlled error handling:

```python
class DomainError(Exception):
    def __init__(self, code: str, message: str, *, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
```

**Error Response Format:**

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "status_code": 401,
    "details": {}
  }
}
```

All unhandled exceptions are caught by a global error handler that logs the error with a request ID and returns a sanitized 500 response to the client.

### Authorization & Role Guards

**Authentication Decorator:**

```python
@require_auth
def protected_endpoint():
    # g.current_user is available
```

**Role-Based Authorization:**

```python
@require_role(Role.MANAGER, Role.ADMIN)
def manager_only_endpoint():
    # Only MANAGER or ADMIN can access
```

**Ownership Validation:**

Some endpoints use `require_ownership` decorators to ensure users can only access their own resources (e.g., only view their own orders).

### Idempotency

Checkout confirmation implements idempotency to prevent duplicate orders:

- Client must send `Idempotency-Key` header with checkout requests
- Server stores request hash and response payload in `idempotency_keys` table
- If duplicate request detected (same key + user + request body), returns cached response
- Idempotency keys expire after 24 hours

### Audit & Logging

**Request Logging:**

All requests are logged with:

- HTTP method and path
- Response status code
- Request duration in milliseconds
- Request ID (for tracing)
- Client IP address

**Audit Logs:**

Critical operations (e.g., order creation, status changes) create audit log entries:

```python
AuditService.create(
    actor_id=current_user.id,
    action="order_created",
    resource_type="Order",
    resource_id=order.id,
    details={"order_number": order.order_number}
)
```

Audit logs are queryable via `/api/v1/admin/audit` (admin-only).

## Authentication & Authorization

### JWT Flow

1. **Registration** (`POST /api/v1/auth/register`):
   - User submits email, password, full name, phone
   - Password is hashed with bcrypt
   - User record created with role (defaults to CUSTOMER)
   - JWT access token and refresh token returned

2. **Login** (`POST /api/v1/auth/login`):
   - User submits email and password
   - Server verifies credentials
   - Returns JWT access token (240 minutes expiry) and refresh token (30 days expiry)

3. **Protected Requests**:
   - Client includes `Authorization: Bearer <token>` header
   - Middleware validates token and loads user into `g.current_user`

4. **Password Reset**:
   - User requests reset (`POST /api/v1/auth/forgot-password`)
   - Server sends email with reset token via Brevo
   - User submits new password with token (`POST /api/v1/auth/reset-password`)

### Role System

Roles are hierarchical but not automatically inherited. Authorization is explicit:

- **CUSTOMER**: Can access `/api/v1/store`, `/api/v1/cart`, `/api/v1/checkout`, `/api/v1/orders`
- **EMPLOYEE**: Can access `/api/v1/ops` (picking, inventory updates)
- **MANAGER**: Can access `/api/v1/admin` (catalog, delivery slots, analytics) + employee routes
- **ADMIN**: Full access to all endpoints including user management and audit logs

### Protected Routes Concept

Routes are protected using decorators:

```python
# Authentication required
@blueprint.get("/profile")
@jwt_required()
def get_profile():
    ...

# Role-based access
@blueprint.post("/admin/users")
@require_role(Role.ADMIN)
def create_user():
    ...
```

## API Design

### API Versioning

All endpoints are prefixed with `/api/v1/`. Future breaking changes would introduce `/api/v2/`.

### Response Envelope Format

**Success Response:**

```json
{
  "data": {
    "id": 123,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Success Response with Pagination:**

```json
{
  "data": [
    { "id": 1, "name": "Product A" },
    { "id": 2, "name": "Product B" }
  ],
  "meta": {
    "total": 50,
    "limit": 20,
    "offset": 0
  }
}
```

### Error Envelope Format

```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "The requested product does not exist",
    "status_code": 404,
    "details": {}
  }
}
```

### Pagination & Filtering Approach

List endpoints support pagination via query parameters:

- `limit`: Number of items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

Example: `GET /api/v1/catalog/products?limit=20&offset=40`

Filtering is supported via query parameters specific to each endpoint:

- `GET /api/v1/catalog/products?category_id=5`
- `GET /api/v1/orders?status=DELIVERED`

Search is supported via `q` parameter:

- `GET /api/v1/catalog/products?q=milk`

### Status Codes Philosophy

The API uses standard HTTP status codes semantically:

- **200 OK**: Successful GET, PUT, DELETE
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful DELETE with no response body (rarely used)
- **400 Bad Request**: Validation error, malformed request
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Authenticated but lacks permission
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Resource conflict (e.g., duplicate email)
- **422 Unprocessable Entity**: Semantic validation error
- **500 Internal Server Error**: Unexpected server error

## Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable                           | Required   | Default                    | Description                                                                          |
| ---------------------------------- | ---------- | -------------------------- | ------------------------------------------------------------------------------------ |
| `DATABASE_URL`                     | Yes        | -                          | PostgreSQL connection string (e.g., `postgresql://user:pass@localhost:5432/mami_db`) |
| `JWT_SECRET_KEY`                   | Yes        | -                          | Secret key for signing JWT tokens (use strong random value)                          |
| `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | No         | 240                        | JWT access token expiration in minutes (4 hours default)                             |
| `CORS_ALLOWED_ORIGINS`             | No         | `*`                        | Comma-separated list of allowed CORS origins (must not be `*` in production)         |
| `FRONTEND_BASE_URL`                | No         | `http://localhost:5173`    | Frontend URL for email links and CORS                                                |
| `DELIVERY_SOURCE_BRANCH_ID`        | Production | -                          | Branch ID to use as delivery fulfillment source                                      |
| `BREVO_API_KEY`                    | Production | -                          | Brevo API key for sending transactional emails                                       |
| `BREVO_SENDER_EMAIL`               | Production | -                          | Verified sender email address in Brevo                                               |
| `BREVO_RESET_TOKEN_OTP_ID`         | No         | -                          | Brevo template ID for password reset emails                                          |
| `BREVO_REGISTER_OTP_ID`            | No         | -                          | Brevo template ID for registration OTP emails                                        |
| `ENABLE_REGISTRATION_OTP`          | No         | `false`                    | Enable OTP verification during registration (`true`/`false`)                         |
| `APP_ENV`                          | No         | `production`               | Environment name (`development`, `production`)                                       |
| `RATE_LIMIT_DEFAULTS`              | No         | `10000 per day, 1000 per hour` | Default rate limit for API endpoints                                             |

### Security Notes

- **Never commit `.env` to version control**
- Use a cryptographically secure random value for `JWT_SECRET_KEY` (32+ characters)
- In production, set `CORS_ALLOWED_ORIGINS` to specific frontend domain(s)
- Use strong database passwords and restrict database access to application server
- Enable SSL/TLS for database connections in production
- Store sensitive environment variables in secure secrets management (e.g., AWS Secrets Manager, Azure Key Vault)

## Database & Migrations

### Database Engine

The application uses **PostgreSQL** (recommended version 13+) via SQLAlchemy ORM. PostgreSQL features utilized:

- JSONB columns for flexible metadata storage
- Indexes for performance optimization
- Foreign key constraints for referential integrity
- Unique constraints for business rules (e.g., unique email, unique cart per user)

### How Migrations Are Managed

Database schema changes are managed using **Alembic**:

1. Models are defined in `app/models/`
2. Schema changes are detected automatically by Alembic
3. Migration scripts are generated in `alembic/versions/`
4. Migrations are applied sequentially to update the database

### How to Run Migrations

**Create a new migration after model changes:**

```bash
alembic revision --autogenerate -m "Add product reviews table"
```

**Review the generated migration** in `alembic/versions/` and edit if needed.

**Apply pending migrations:**

```bash
alembic upgrade head
```

**Rollback the last migration:**

```bash
alembic downgrade -1
```

**View migration history:**

```bash
alembic history
```

### Seed / Initial Data

Initial data seeding scripts are located in `scripts/seed/`. To seed the database:

1. Ensure migrations are up to date: `alembic upgrade head`
2. Run seed scripts (if available):

```bash
python -m scripts.seed.seed
```

Seed scripts create:

- Branches, categories, ~180 products (with product photos)
- Inventory, users, addresses, delivery slots
- Sample carts, orders, stock requests, and audit logs

## Local Development

### Prerequisites

- **Python 3.11+** (check with `python --version`)
- **PostgreSQL 13+** (local instance or Docker)
- **pip** or **poetry** for dependency management
- **Git** for version control

### Virtual Environment Setup

1. **Clone the repository:**

```bash
git clone <repository-url>
cd mami-supermarket-backend
```

2. **Create virtual environment:**

```bash
python -m venv venv
```

3. **Activate virtual environment:**

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Setup

1. **Create PostgreSQL database:**

```bash
createdb mami_supermarket_dev
```

2. **Create `.env` file:**

```bash
cp .env.example .env  # If example exists, otherwise create manually
```

Edit `.env` and set:

```
DATABASE_URL=postgresql://localhost:5432/mami_supermarket_dev
JWT_SECRET_KEY=your-super-secret-key-here
APP_ENV=development
CORS_ALLOWED_ORIGINS=http://localhost:5173
ENABLE_REGISTRATION_OTP=false
```

3. **Run migrations:**

```bash
alembic upgrade head
```

4. **Seed database (optional):**

```bash
python -m scripts.seed.seed
```

### Run the Server

**Development server (Flask built-in):**

```bash
python run.py
```

Server runs on `http://localhost:5000` by default.

**Development with auto-reload:**

```bash
FLASK_APP=app flask run --reload
```

### Common Dev Commands

| Command                                        | Description                     |
| ---------------------------------------------- | ------------------------------- |
| `python run.py`                                | Start development server        |
| `alembic upgrade head`                         | Apply all pending migrations    |
| `alembic revision --autogenerate -m "message"` | Create new migration            |
| `pytest`                                       | Run all tests                   |
| `pytest tests/auth/`                           | Run specific test module        |
| `pytest --cov=app`                             | Run tests with coverage report  |
| `ruff check .`                                 | Run linter (if ruff configured) |
| `python -m flask shell`                        | Open Flask shell for debugging  |

## Testing

### Test Structure

Tests are organized by domain in the `tests/` directory:

```
tests/
├── conftest.py              # Shared fixtures
├── auth/                    # Authentication tests
├── cart/                    # Cart tests
├── catalog/                 # Catalog tests
├── checkout/                # Checkout tests
├── orders/                  # Order tests
├── ops/                     # Operations tests
├── admin/                   # Admin endpoint tests
├── profile/                 # Profile management tests
└── infrastructure/          # Middleware and utility tests
```

### How to Run Tests

**Run all tests:**

```bash
pytest
```

**Run specific test file:**

```bash
pytest tests/auth/test_auth.py
```

**Run with coverage:**

```bash
pytest --cov=app --cov-report=html
```

Coverage report generated in `htmlcov/index.html`.

**Run specific test function:**

```bash
pytest tests/cart/test_cart.py::test_add_item_to_cart
```

**Run with verbose output:**

```bash
pytest -v
```

### What Is Covered

The test suite covers:

- **Authentication**: Registration, login, password reset, JWT validation
- **Authorization**: Role-based access control, ownership validation
- **Cart Operations**: Add/remove items, quantity updates, inventory validation
- **Catalog**: Product listing, category filtering, search
- **Checkout**: Preview calculation, order confirmation, idempotency
- **Orders**: Order creation, status updates, cancellation, picking workflows
- **Admin Operations**: User management, catalog management, branch configuration
- **Profile Management**: Address CRUD, default address, phone updates
- **Stock Requests**: Employee requests, manager approval/rejection
- **Audit Logging**: Critical action tracking
- **Error Handling**: Validation errors, domain errors, HTTP exceptions

Current test coverage is documented in `tests/DB_TEST_COVERAGE.md`.

## Production Notes

### Deployment Assumptions

The backend is designed to be deployed as a WSGI application:

- **WSGI Server**: Gunicorn (started via `start.sh`)
- **Reverse Proxy**: Nginx (recommended) for SSL termination and static file serving
- **Database**: Managed PostgreSQL service (AWS RDS, Azure Database, etc.)
- **Process Manager**: systemd, Docker, or Kubernetes
- **Environment Variables**: Injected via platform secrets (Render, Heroku, AWS, etc.)

**Sample Gunicorn command:**

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
```

### Security Considerations

**Before Production Deployment:**

1. **JWT Secret**: Use cryptographically secure random value (32+ bytes)
2. **CORS**: Set `CORS_ALLOWED_ORIGINS` to specific frontend domain(s) (never `*`)
3. **HTTPS Only**: Enforce HTTPS in production (use Nginx or platform SSL)
4. **Database Connections**: Use SSL/TLS for PostgreSQL connections
5. **Rate Limiting**: Ensure `RATE_LIMIT_DEFAULTS` is configured appropriately
6. **Secrets Management**: Use platform secrets for sensitive environment variables
7. **Disable Debug Mode**: Ensure `debug=False` in production WSGI config
8. **Security Headers**: Middleware adds CSP, HSTS, X-Frame-Options automatically
9. **Input Validation**: All requests validated via Pydantic schemas
10. **SQL Injection**: Protected by SQLAlchemy parameterized queries

**Additional Recommendations:**

- Implement IP whitelisting for admin endpoints if internal-only
- Enable database query logging for security audit
- Set up intrusion detection and monitoring (e.g., AWS GuardDuty)
- Regularly update dependencies (`pip install --upgrade`)
- Use secrets rotation policies for JWT keys and API keys

### Things to Configure Before Production

| Configuration               | Action Required                                            |
| --------------------------- | ---------------------------------------------------------- |
| `DATABASE_URL`              | Set to production PostgreSQL connection string (with SSL)  |
| `JWT_SECRET_KEY`            | Generate secure random key (never reuse dev key)           |
| `CORS_ALLOWED_ORIGINS`      | Set to production frontend URL(s)                          |
| `BREVO_API_KEY`             | Set production Brevo API key                               |
| `BREVO_SENDER_EMAIL`        | Use verified production sender email                       |
| `DELIVERY_SOURCE_BRANCH_ID` | Set to production branch ID                                |
| `APP_ENV`                   | Set to `production`                                        |
| Database Migrations         | Run `alembic upgrade head` on production database          |
| Initial Data                | Run seed scripts to create initial admin user and branches |
| Monitoring                  | Set up application monitoring (Sentry, Datadog, etc.)      |
| Logging                     | Configure log aggregation (CloudWatch, ELK, etc.)          |
| Backups                     | Enable automated database backups                          |
| Health Checks               | Configure platform health check to `/health`               |

**Deployment Checklist:**

- [ ] All environment variables set and validated
- [ ] Database migrations applied
- [ ] Initial admin user created
- [ ] CORS configured for production frontend
- [ ] Rate limiting enabled
- [ ] SSL/TLS certificates configured
- [ ] Security headers verified
- [ ] Health check endpoint responding
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery plan in place

---

## Additional Resources

- **API Documentation**: Consider generating OpenAPI/Swagger docs
- **Postman Collection**: Import collection for API testing
- **Architecture Diagrams**: See `docs/` folder (if available)
- **Contributing Guide**: See `CONTRIBUTING.md` (if available)

For questions or issues, contact the development team or create an issue in the repository.
