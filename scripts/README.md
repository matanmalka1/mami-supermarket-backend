# Seed Scripts

סקריפטים למילוי מסד הנתונים בנתוני פיתוח ריאליסטיים.

## שימוש

### הרצת seed מלא

```bash
python scripts/seed.py
```

הסקריפט:

- יוצר את כל הטבלאות אם הן לא קיימות
- ממלא את כל הטבלאות בנתונים
- **idempotent** - בטוח להריץ מספר פעמים (לא יוצר כפילויות)

### סדר הטעינה

1. **Branches** - 5 סניפים בערים שונות בישראל
2. **Categories** - 11 קטגוריות מוצרים
3. **Products** - מוצרים עם SKU, מחיר ותיאור
4. **Users** - לקוחות, עובדים, מנהלים ואדמין
5. **Addresses** - כתובות ישראליות ריאליסטיות
6. **Delivery Slots** - משבצות זמני משלוח (6 משבצות ליום, כל השבוע)
7. **Inventory** - מלאי לכל שילוב של סניף×מוצר
8. **Carts** - עגלות קניות פעילות ללקוחות
9. **Orders** - הזמנות עם פריטים, delivery/pickup
10. **Payment Tokens** - טוקני תשלום מדומים
11. **Stock Requests** - בקשות עדכון מלאי
12. **Idempotency Keys** - מפתחות למניעת כפילויות

## משתמשים שנוצרים

### לקוחות

- `noam.levi@example.com`
- `yael.cohen@example.com`
- `itamari.ben@example.com`

### צוות

- `employee1@mami.local` (עובד)
- `manager@mami.local` (מנהל)
- `admin@mami.local` (אדמין)

**סיסמה לכולם**: `Mami2026!`

## קבצים

- `seed.py` - סקריפט ראשי
- `seed/seed_branches.py` - סניפים
- `seed/seed_categories.py` - קטגוריות
- `seed/seed_products.py` - מוצרים
- `seed/seed_users.py` - משתמשים
- `seed/seed_address.py` - כתובות
- `seed/seed_delivery_slots.py` - משבצות זמני משלוח
- `seed/seed_inventory.py` - מלאי
- `seed/seed_carts.py` - עגלות קניות
- `seed/seed_orders.py` - הזמנות
- `seed/seed_payment_tokens.py` - טוקני תשלום
- `seed/seed_stock_request.py` - בקשות מלאי
- `seed/seed_idempotency_keys.py` - מפתחות idempotency

## הערות

- כל הפונקציות הן **idempotent** - בטוח להריץ שוב
- נתונים קיימים לא נמחקים, רק מתעדכנים במידת הצורך
- כל קובץ ניתן לייבא ולהריץ בנפרד אם צריך

## פיתוח

כל פונקציית seed מקבלת `Session` ומחזירה רשימת אובייקטים שנוצרו/עודכנו.

דוגמה:

```python
from scripts.seed.seed_branches import seed_branches

branches = seed_branches(session)
session.commit()
```
