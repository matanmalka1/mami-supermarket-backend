# seed/seed_products.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product  # TODO: adjust import path
from app.models.category import Category


def _ensure_product(
    session: Session,
    *,
    sku: str,
    name: str,
    category_id,
    price: str,
    description: str | None = None,
    unit: str,
    bin_location: str,
    image_url: str,
) -> Product:
    p = session.execute(
        select(Product).where(Product.sku == sku)
    ).scalar_one_or_none()

    if p:
        updated = False
        if hasattr(p, "is_active") and p.is_active is False:
            p.is_active = True
            updated = True
        if p.name != name:
            p.name = name
            updated = True
        if p.category_id != category_id:
            p.category_id = category_id
            updated = True
        if str(p.price) != str(price):
            p.price = price
            updated = True
        if p.description != description:
            p.description = description
            updated = True
        if getattr(p, "unit", None) != unit:
            p.unit = unit
            updated = True
        if getattr(p, "bin_location", None) != bin_location:
            p.bin_location = bin_location
            updated = True
        if getattr(p, "image_url", None) != image_url:
            p.image_url = image_url
            updated = True
        if updated:
            session.add(p)
        return p
    p = Product(
        sku=sku,
        name=name,
        category_id=category_id,
        price=price,
        description=description,
        unit=unit,
        bin_location=bin_location,
        image_url=image_url,
    )
    session.add(p)
    return p


def seed_products(session: Session) -> list[Product]:
    categories = session.execute(select(Category)).scalars().all()
    category_by_name = {c.name: c for c in categories}
    def cat_id(category_name: str):
        c = category_by_name.get(category_name)
        if not c:
            raise RuntimeError(f"Category not found: {category_name}. Seed categories first.")
        return c.id
    products_data = [
        # Fruits & Vegetables
        ("FRU-APL-GALA-1KG", "Apples Gala 1kg", "Fruits & Vegetables", "12.90", "Fresh Gala apples (1kg)."),
        ("VEG-TOM-1KG", "Tomatoes 1kg", "Fruits & Vegetables", "9.90", "Fresh tomatoes (1kg)."),
        ("VEG-CUC-1KG", "Cucumbers 1kg", "Fruits & Vegetables", "8.50", "Fresh cucumbers (1kg)."),
        # Dairy & Eggs
        ("DAR-MILK-3PCT-1L", "Milk 3% 1L", "Dairy & Eggs", "6.20", "Pasteurized milk 3% (1 liter)."),
        ("DAR-YOG-PLAIN-200G", "Yogurt Plain 200g", "Dairy & Eggs", "3.90", "Plain yogurt (200g)."),
        ("DAR-EGGS-L-12", "Eggs L 12 pack", "Dairy & Eggs", "14.90", "Large eggs (12)."),
        # Bakery
        ("BAK-BREAD-WHITE-750G", "White Bread 750g", "Bakery", "9.50", "Sliced white bread (750g)."),
        ("BAK-PITA-10", "Pita Bread 10 pack", "Bakery", "8.90", "Fresh pita bread (10 units)."),
        # Beverages
        ("BEV-WATER-1P5L", "Mineral Water 1.5L", "Beverages", "4.50", "Mineral water bottle (1.5L)."),
        ("BEV-COLA-1P5L", "Cola 1.5L", "Beverages", "8.90", "Sparkling cola drink (1.5L)."),
        ("BEV-ORANGE-JUICE-1L", "Orange Juice 1L", "Beverages", "11.90", "Orange juice (1L)."),
        # Pantry
        ("PAN-PASTA-SPAGH-500G", "Pasta Spaghetti 500g", "Pantry", "6.90", "Spaghetti pasta (500g)."),
        ("PAN-RICE-1KG", "Rice 1kg", "Pantry", "8.90", "White rice (1kg)."),
        ("PAN-TUNA-160G", "Tuna Can 160g", "Pantry", "7.50", "Canned tuna (160g)."),
        ("PAN-TOMATO-SAUCE-500G", "Tomato Sauce 500g", "Pantry", "5.90", "Tomato sauce (500g)."),
        # Snacks
        ("SNK-CHIPS-CLASSIC-70G", "Potato Chips Classic 70g", "Snacks", "6.50", "Classic potato chips (70g)."),
        ("SNK-NUTS-ALMOND-200G", "Almonds 200g", "Snacks", "18.90", "Roasted almonds (200g)."),
        # Household
        ("HOU-TISSUE-12", "Toilet Paper 12 rolls", "Household", "29.90", "Toilet paper pack (12 rolls)."),
        ("HOU-DISH-SOAP-750ML", "Dish Soap 750ml", "Household", "12.90", "Dishwashing liquid (750ml)."),
        # Personal Care
        ("PER-SHAMPOO-500ML", "Shampoo 500ml", "Personal Care", "19.90", "Shampoo bottle (500ml)."),
        ("PER-SOAP-BAR-4", "Soap Bars 4 pack", "Personal Care", "9.90", "Soap bars (4 units)."),
    ]
    created: list[Product] = []
    for idx, (sku, name, category_name, price, desc) in enumerate(products_data):
        bin_location = f"A-{idx+1:02d}"
        image_url = "https://placehold.co/600x600"
        unit = "unit"
        created.append(
            _ensure_product(
                session,
                sku=sku,
                name=name,
                category_id=cat_id(category_name),
                price=price,
                description=desc,
                unit=unit,
                bin_location=bin_location,
                image_url=image_url,
            )
        )
    session.flush()
    return created