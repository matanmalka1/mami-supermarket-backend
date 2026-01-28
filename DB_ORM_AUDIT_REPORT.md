# Database Usage & ORM Audit Report

## Section 1: Findings

### 1. Query Efficiency & N+1

- Most service queries use `selectinload` for related collections (e.g., Order.items, Cart.items), reducing N+1 risk.
- No evidence of N+1 in main endpoints, but some relationships default to lazy loading (e.g., Product.category, CartItem.product) and may cause N+1 if accessed in bulk.

### 2. Transaction Usage

- Transactions are used for critical updates (e.g., order cancellation uses `with_for_update` and explicit commit).
- No misuse of transactions found, but not all service methods show explicit rollback handling on error.

### 3. Delete Strategies

- Business entities (User, Product, Category) use `SoftDeleteMixin` (`is_active` flag).
- Technical entities (OrderItem, CartItem, Inventory) use `cascade="all, delete-orphan"` for parent-child relationships.
- Some entities (e.g., Address) do not use soft delete, which is correct for technical/auxiliary data.

### 4. Model-to-DB Mapping

- Models use explicit constraints (unique, not null, foreign keys).
- Alembic migrations should be checked for full alignment (not covered in this audit).

## Section 2: Risk Level

- **Query Efficiency:** Low (N+1 risk only if new code accesses lazy relationships in bulk).
- **Transaction Usage:** Medium (lack of explicit rollback in some flows could risk data consistency).
- **Delete Strategies:** Low (soft/cascade applied per business/technical domain, but review for new models).
- **Model Mapping:** Low (well-defined, but migration drift possible if not regularly checked).

## Section 3: Suggested Fix (No Code)

- Audit all endpoints for bulk access to lazy relationships; use eager loading where needed.
- Ensure all transactional service methods handle rollback on error.
- Periodically review Alembic migrations for drift from models.
- For new business entities, default to soft delete; for technical, use cascade.
- Add DB tests for all points in `DB_TEST_COVERAGE.md`.

---

This report summarizes the current state and provides actionable recommendations for maintaining high-quality DB usage and ORM practices.
