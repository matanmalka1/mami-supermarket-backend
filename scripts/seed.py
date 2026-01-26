from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Ensure app imports work when running as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env file
load_dotenv(PROJECT_ROOT / ".env")

from app.config import AppConfig
from app.models import Base

# Import all seed functions
from scripts.seed.seed_branches import seed_branches
from scripts.seed.seed_categories import seed_categories
from scripts.seed.seed_products import seed_products
from scripts.seed.seed_users import seed_users
from scripts.seed.seed_address import seed_addresses
from scripts.seed.seed_delivery_slots import seed_delivery_slots
from scripts.seed.seed_inventory import seed_inventory
from scripts.seed.seed_carts import seed_carts
from scripts.seed.seed_orders import seed_orders
from scripts.seed.seed_payment_tokens import seed_payment_tokens
from scripts.seed.seed_stock_request import seed_stock_requests
from scripts.seed.seed_idempotency_keys import seed_idempotency_keys


def run_seed(session: Session) -> None:
    print("🌱 Starting database seed...")
    
    # 1. Branches (must be first - needed by many other tables)
    print("  → Seeding branches...")
    branches = seed_branches(session)
    print(f"    ✓ {len(branches)} branches")
    
    # 2. Categories (needed by products)
    print("  → Seeding categories...")
    categories = seed_categories(session)
    print(f"    ✓ {len(categories)} categories")
    
    # 3. Products (needed by inventory, cart, orders)
    print("  → Seeding products...")
    products = seed_products(session)
    print(f"    ✓ {len(products)} products")
    
    # 4. Users (needed by addresses, carts, orders, tokens)
    print("  → Seeding users...")
    default_branch_id = branches[0].id if branches else None
    users = seed_users(session, default_branch_id=default_branch_id)
    print(f"    ✓ {len(users)} users")
    
    # 5. Addresses (needs users)
    print("  → Seeding addresses...")
    user_ids = [u.id for u in users]
    addresses = seed_addresses(session, user_ids=user_ids)
    print(f"    ✓ {len(addresses)} addresses")
    
    # 6. Delivery Slots (needs branches)
    print("  → Seeding delivery slots...")
    slots = seed_delivery_slots(session)
    print(f"    ✓ {len(slots)} delivery slots")
    
    # 7. Inventory (needs products + branches)
    print("  → Seeding inventory...")
    inventory_items = seed_inventory(session)
    print(f"    ✓ {len(inventory_items)} inventory records")
    
    # 8. Carts (needs users + products)
    print("  → Seeding carts...")
    carts = seed_carts(session)
    print(f"    ✓ {len(carts)} carts")
    
    # 9. Orders (needs users, products, branches, delivery slots, addresses)
    print("  → Seeding orders...")
    orders = seed_orders(session)
    print(f"    ✓ {len(orders)} orders")
    
    # 10. Payment Tokens (needs users)
    print("  → Seeding payment tokens...")
    tokens = seed_payment_tokens(session)
    print(f"    ✓ {len(tokens)} payment tokens")
    
    # 11. Stock Requests (needs branches, products, users)
    print("  → Seeding stock requests...")
    stock_reqs = seed_stock_requests(session)
    print(f"    ✓ {len(stock_reqs)} stock requests")
    
    # 12. Idempotency Keys (needs users)
    print("  → Seeding idempotency keys...")
    idem_keys = seed_idempotency_keys(session)
    print(f"    ✓ {len(idem_keys)} idempotency keys")
    
    print("✅ Database seed completed successfully!")

    # --- Verification step ---
    from sqlalchemy import text
    null_icon_slug = session.execute(text("SELECT COUNT(*) FROM categories WHERE icon_slug IS NULL")).scalar()
    null_product_fields = session.execute(text("SELECT COUNT(*) FROM products WHERE image_url IS NULL OR bin_location IS NULL OR unit IS NULL")).scalar()
    print(f"[Verification] categories with null icon_slug: {null_icon_slug}")
    print(f"[Verification] products with null image_url/bin_location/unit: {null_product_fields}")
    if null_icon_slug != 0 or null_product_fields != 0:
        raise RuntimeError("Seed verification failed: DB contains nulls in required fields. See counts above.")


def main() -> None:
    """Main entry point."""
    config = AppConfig()
    engine = create_engine(config.DATABASE_URL)
    
    # Create all tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(engine)
    
    try:
        with Session(engine) as session:
            run_seed(session)
            session.commit()
            print("💾 Changes committed to database")
    except Exception as e:
        print(f"❌ Error during seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
