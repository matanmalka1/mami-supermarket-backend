# from __future__ import annotations
# import os
# from datetime import datetime, timedelta, time
# from uuid import UUID
# from passlib.context import CryptContext
# from sqlalchemy.orm import Session
# from app.models import (
#     Address,
#     Branch,
#     Cart,
#     CartItem,
#     CartStatus,
#     Category,
#     DeliverySlot,
#     FulfillmentType,
#     Inventory,
#     Order,
#     OrderDeliveryDetails,
#     OrderItem,
#     OrderStatus,
#     Product,
#     Role,
#     User,
# )

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")
# SAMPLE_USERS = [
#     ("customer@mami.local", "Customer One", "Customer123!", Role.CUSTOMER),
#     ("employee@mami.local", "Employee One", "Employee123!", Role.EMPLOYEE),
#     ("manager@mami.local", "Manager One", "Manager123!", Role.MANAGER),
# ]
# CATALOG = {
#     "Dairy": [("Whole Milk 1L", "MILK-1L", 5.90, "Fresh whole milk"), ("Greek Yogurt", "YOG-GREEK", 7.50, "Thick Greek yogurt")],
#     "Bakery": [("Sourdough Bread", "BREAD-SOUR", 12.00, "Crusty sourdough loaf"), ("Butter Croissant", "CROISS-BUT", 6.50, "Buttery flaky croissant")],
#     "Produce": [("Bananas", "BAN-1KG", 4.20, "Fresh bananas (1kg)"), ("Cherry Tomatoes", "TOM-CHERRY", 8.30, "Sweet cherry tomatoes")],
# }

# def _get_or_create(session: Session, model, defaults=None, **filters):
#     found = session.query(model).filter_by(**filters).first()
#     if found:
#         return found
#     instance = model(**(defaults or {}), **filters)
#     session.add(instance)
#     session.flush()
#     return instance

# def _seed_branches(session: Session, config) -> tuple[Branch, Branch]:
#     branch_id = None
#     if config.DELIVERY_SOURCE_BRANCH_ID:
#         try:
#             branch_id = UUID(str(config.DELIVERY_SOURCE_BRANCH_ID))
#         except ValueError:
#             branch_id = None
#     warehouse = _get_or_create(session, Branch, defaults={"id": branch_id, "address": "Central warehouse, main street"}, name="The Warehouse")
#     store = _get_or_create(session, Branch, defaults={"address": "Downtown street 5"}, name="Downtown Branch")
#     return warehouse, store

# def _seed_delivery_slots(session: Session, branch: Branch) -> None:
#     existing = {(s.day_of_week, s.start_time, s.end_time) for s in session.query(DeliverySlot).filter_by(branch_id=branch.id)}
#     for day in range(7):
#         for start in range(6, 22, 2):
#             slot_start, slot_end = time(start, 0), time(start + 2, 0)
#             if (day, slot_start, slot_end) not in existing:
#                 session.add(DeliverySlot(branch_id=branch.id, day_of_week=day, start_time=slot_start, end_time=slot_end))

# def _seed_users(session: Session, default_branch_id: UUID) -> None:
#     admin_email, admin_pwd, admin_name = (
#         os.environ.get("ADMIN_EMAIL", "admin@mami.local"),
#         os.environ.get("ADMIN_PASSWORD", "ChangeMe123!"),
#         os.environ.get("ADMIN_FULL_NAME", "Super Admin"),
#     )
#     _get_or_create(session, User, email=admin_email, defaults={"full_name": admin_name, "password_hash": pwd_context.hash(admin_pwd), "role": Role.ADMIN})
#     for email, full_name, password, role in SAMPLE_USERS:
#         _get_or_create(
#             session,
#             User,
#             email=email,
#             defaults={"full_name": full_name, "password_hash": pwd_context.hash(password), "role": role, "default_branch_id": default_branch_id},
#         )

# def _seed_addresses(session: Session, target: int = 30) -> None:
#     users = session.query(User).all()
#     existing = session.query(Address).count()
#     for idx in range(existing, target):
#         session.add(Address(user_id=users[idx % len(users)].id, address_line=f"{idx + 1} Main Street", city="Tel Aviv", country="Israel", postal_code=f"60{101 + idx:03d}"))

# def _seed_catalog(session: Session) -> list[Product]:
#     products: list[Product] = []
#     for cat_name, items in CATALOG.items():
#         category = _get_or_create(session, Category, defaults={"description": f"{cat_name} items"}, name=cat_name)
#         for name, sku, price, desc in items:
#             products.append(_get_or_create(session, Product, defaults={"price": price, "description": desc, "category_id": category.id}, sku=sku, name=name))
#     return products

# def _seed_carts(session: Session, products: list[Product]) -> None:
#     for customer in session.query(User).filter_by(role=Role.CUSTOMER).all():
#         cart = _get_or_create(session, Cart, defaults={"status": CartStatus.ACTIVE}, user_id=customer.id)
#         existing_items = {item.product_id for item in cart.items}
#         for idx, product in enumerate(products[:3], start=1):
#             if product.id in existing_items:
#                 continue
#             session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=1 + (idx % 2), unit_price=product.price))

# def _seed_orders(session: Session, branch: Branch, products: list[Product]) -> None:
#     customers = session.query(User).filter_by(role=Role.CUSTOMER).all()
#     slot = session.query(DeliverySlot).filter_by(branch_id=branch.id).first()
#     if not customers or not products or not slot:
#         return
#     existing = session.query(Order).count()
#     for idx in range(existing, 5):
#         user = customers[idx % len(customers)]
#         address = session.query(Address).filter_by(user_id=user.id).first()
#         items = [{"product": p, "quantity": 1 + (idx % 2), "unit_price": p.price} for p in products[:2]]
#         total_amount = sum(item["unit_price"] * item["quantity"] for item in items)
#         order = Order(
#             order_number=f"ORD-{idx + 1:04d}",
#             user_id=user.id,
#             total_amount=total_amount,
#             fulfillment_type=FulfillmentType.DELIVERY,
#             status=OrderStatus.CREATED,
#             branch_id=branch.id,
#         )
#         session.add(order)
#         session.flush()
        
#         for item in items:
#             session.add(OrderItem(order_id=order.id, product_id=item["product"].id, name=item["product"].name, sku=item["product"].sku, unit_price=item["unit_price"], quantity=item["quantity"]))
#         slot_date = datetime.utcnow().date() + timedelta(days=idx + 1)
#         session.add(
#             OrderDeliveryDetails(
#                 order_id=order.id,
#                 delivery_slot_id=slot.id,
#                 address=address.address_line if address else f"{idx + 1} Sample Street",
#                 slot_start=datetime.combine(slot_date, slot.start_time),
#                 slot_end=datetime.combine(slot_date, slot.end_time),
#             )
#         )
# def run_seed(session: Session, config) -> None:
#     warehouse, store = _seed_branches(session, config)
#     _seed_delivery_slots(session, warehouse)
#     _seed_users(session, warehouse.id)
#     products = _seed_catalog(session)

#     for idx, product in enumerate(products, start=1):
#         qty = 20 + idx * 5
#         for branch in (warehouse, store):
#             _get_or_create(session, Inventory, defaults={"available_quantity": qty, "reserved_quantity": 0}, product_id=product.id, branch_id=branch.id)

#     _seed_addresses(session)
#     _seed_carts(session, products)
#     _seed_orders(session, warehouse, products)
