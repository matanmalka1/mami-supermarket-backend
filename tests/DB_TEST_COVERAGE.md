# Essential DB Test Coverage Points

1. **CRUD Operations**
   - Create, read, update, and delete for all business entities (e.g., User, Order, Product, Cart, Category).
   - Ensure soft delete sets `is_active` to False for business entities.
   - Ensure CASCADE deletes for technical entities (e.g., CartItem, OrderItem, Inventory).

2. **Relationship Integrity**
   - Foreign key constraints are enforced (e.g., deleting a user with orders/carts/wishlist).
   - Orphan removal for `delete-orphan` relationships.
   - Eager/lazy loading returns expected related data.

3. **Transaction Handling**
   - Rollback on error leaves DB in consistent state.
   - Committed transactions persist all changes.

4. **Unique & Not Null Constraints**
   - Unique constraints (e.g., email, SKU, category name) are enforced.
   - Not null constraints are enforced for required fields.

5. **Soft Delete & Cascade**
   - Soft delete does not physically remove business records.
   - Cascade delete removes technical children when parent is deleted.

6. **Data Consistency**
   - Updates to parent/child entities propagate as expected.
   - No orphaned records after delete operations.

7. **Query Performance**
   - N+1 queries are not present in common endpoints.
   - Eager loading is used where needed.

8. **Migration Consistency**
   - Alembic migrations match model definitions.
   - No missing/extra columns or constraints.

9. **Edge Cases**
   - Deleting entities with/without children.
   - Bulk operations (batch insert/update/delete).

10. **Security**
    - No unauthorized access to other users’ data via queries.

---

This list should be used to guide DB-related test writing and coverage review.
