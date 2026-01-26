# seed/seed_categories.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category 

def _ensure_category(session: Session, *, name: str, description: str | None, icon_slug: str) -> Category:
    cat = session.execute(
        select(Category).where(Category.name == name)
    ).scalar_one_or_none()

    if cat:
        updated = False

        if hasattr(cat, "is_active") and cat.is_active is False:
            cat.is_active = True
            updated = True

        if cat.description != description:
            cat.description = description
            updated = True

        if getattr(cat, "icon_slug", None) != icon_slug:
            cat.icon_slug = icon_slug
            updated = True

        if updated:
            session.add(cat)
        return cat

    cat = Category(name=name, description=description, icon_slug=icon_slug)
    session.add(cat)
    return cat


def seed_categories(session: Session) -> list[Category]:
    categories_data = [
        ("Fruits & Vegetables", "Fresh produce: fruits, vegetables, herbs.", "produce"),
        ("Dairy & Eggs", "Milk, yogurt, cheese, eggs, butter.", "dairy"),
        ("Meat & Fish", "Fresh meat, poultry, fish, deli meats.", "meat"),
        ("Bakery", "Bread, rolls, pastries, cakes.", "bakery"),
        ("Frozen", "Frozen vegetables, ice cream, frozen meals.", "frozen"),
        ("Beverages", "Water, soft drinks, juice, energy drinks.", "drinks"),
        ("Snacks", "Chips, crackers, nuts, bars.", "snacks"),
        ("Pantry", "Pasta, rice, canned food, sauces, spices.", "pantry"),
        ("Breakfast", "Cereal, spreads, jams, honey.", "breakfast"),
        ("Household", "Paper goods, cleaning supplies.", "household"),
        ("Personal Care", "Shampoo, soap, deodorant, skincare.", "personal_care"),
    ]

    created: list[Category] = []
    for name, desc, icon_slug in categories_data:
        created.append(_ensure_category(session, name=name, description=desc, icon_slug=icon_slug))

    session.flush()
    return created