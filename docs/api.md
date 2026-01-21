## API Notes & Samples

Manual, lightweight reference for common flows and error handling.

### Error Contract (all endpoints)
```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```
- 401 when auth is missing/invalid, 403 on role violations, 404 on ownership mismatch, 409 on business conflicts.

### Auth
**POST /api/v1/auth/login**
```json
// request
{ "email": "u@example.com", "password": "secret123" }

// response
{
  "data": {
    "user": { "id": "...", "email": "u@example.com", "full_name": "User", "role": "CUSTOMER" },
    "access_token": "jwt",
    "refresh_token": null,
    "expires_at": "2026-01-20T12:00:00Z"
  }
}
```
Rate limited (5/min). Login success/failure audited.

### Cart
**POST /api/v1/cart/items**
```json
// request (JWT)
{ "product_id": "<uuid>", "quantity": 2 }

// response
{ "data": { "id": "<cart_id>", "items": [ { "product_id": "...", "quantity": 2, "unit_price": "10.00" } ] } }
```
Validations: product active, quantity>=1, fail if OUT_OF_STOCK_ANYWHERE.

### Checkout
**POST /api/v1/checkout/preview**
```json
{ "cart_id": "<uuid>", "fulfillment_type": "PICKUP", "branch_id": "<uuid>" }
```
Returns missing items and delivery fee (if delivery).

**POST /api/v1/checkout/confirm**
Headers: `Idempotency-Key: <key>`
```json
{
  "cart_id": "<uuid>",
  "payment_token_id": "<uuid>",
  "fulfillment_type": "DELIVERY",
  "delivery_slot_id": "<uuid>",
  "address": "Street 1",
  "save_as_default": true
}
```
- Locks inventory (FOR UPDATE), charges after lock, creates order, decrements stock, audits in-transaction.
- Idempotency: same key+payload returns stored response; different payload → 409.
- Danger zone logged if payment succeeded but commit failed.

### Orders (customer)
- `GET /api/v1/orders?limit=&offset=` paginated list
- `POST /api/v1/orders/:id/cancel` only if status=CREATED; audit cancellation.

### Ops (employee/manager/admin)
- `GET /api/v1/ops/orders?status=&dateFrom=&dateTo=&limit=&offset=` (urgency sorted)
- `PATCH /api/v1/ops/orders/:id/items/:itemId/picked-status` with `{ "picked_status": "PICKED" }`
- `PATCH /api/v1/ops/orders/:id/status` with `{ "status": "READY" }`
Employee transitions enforced; audits on item/status changes.

### Stock Requests
- Employee: `POST /api/v1/stock-requests` `{ "branch_id": "...", "product_id": "...", "quantity": 5, "request_type": "ADD_QUANTITY" }`
- Manager/Admin: `PATCH /api/v1/stock-requests/admin/:id/review` `{ "status": "APPROVED", "approved_quantity": 5 }`
- Bulk: `PATCH /api/v1/stock-requests/admin/bulk-review` with list of items (partial success returned).

### Error Handling Rules for Frontend
- If response has `error.code`, show `message`; branch on code:
  - `AUTH_REQUIRED` → redirect to login
  - `AUTHORIZATION_ERROR` → show “no permission”
  - `NOT_FOUND` on owned resources → treat as missing/expired
  - `INVALID_STATUS_TRANSITION`, `INSUFFICIENT_STOCK`, `IDEMPOTENCY_CONFLICT` → show non-blocking toast; allow retry where sensible
- For validation errors (`VALIDATION_ERROR`), map `error.details.errors` to form fields.
