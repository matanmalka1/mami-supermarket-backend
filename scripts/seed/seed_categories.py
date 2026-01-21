# seed/seed_categories.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category  # TODO: adjust import path


def _ensure_category(session: Session, *, name: str, description: str | None) -> Category:
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

        if updated:
            session.add(cat)
        return cat

    cat = Category(name=name, description=description)
    session.add(cat)
    return cat


def seed_categories(session: Session) -> list[Category]:
    categories_data = [
        ("Fruits & Vegetables", "Fresh produce: fruits, vegetables, herbs."),
        ("Dairy & Eggs", "Milk, yogurt, cheese, eggs, butter."),
        ("Meat & Fish", "Fresh meat, poultry, fish, deli meats."),
        ("Bakery", "Bread, rolls, pastries, cakes."),
        ("Frozen", "Frozen vegetables, ice cream, frozen meals."),
        ("Beverages", "Water, soft drinks, juice, energy drinks."),
        ("Snacks", "Chips, crackers, nuts, bars."),
        ("Pantry", "Pasta, rice, canned food, sauces, spices."),
        ("Breakfast", "Cereal, spreads, jams, honey."),
        ("Household", "Paper goods, cleaning supplies."),
        ("Personal Care", "Shampoo, soap, deodorant, skincare."),
    ]

    created: list[Category] = []
    for name, desc in categories_data:
        created.append(_ensure_category(session, name=name, description=desc))

    session.flush()
    return created