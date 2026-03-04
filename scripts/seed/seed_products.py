# seed/seed_products.py
from __future__ import annotations

import random
import re
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:32] or "item"


# Map product base names to real Unsplash photo IDs (stable CDN URLs)
_PRODUCT_IMAGES: dict[str, str] = {
    # Fruits & Vegetables
    "Apples Gala":            "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=600&h=600&fit=crop",
    "Apples Granny Smith":    "https://images.unsplash.com/photo-1576179635662-9d1983e97e1e?w=600&h=600&fit=crop",
    "Bananas":                "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600&h=600&fit=crop",
    "Oranges":                "https://images.unsplash.com/photo-1547514701-42782101795e?w=600&h=600&fit=crop",
    "Mandarins":              "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab12?w=600&h=600&fit=crop",
    "Tomatoes":               "https://images.unsplash.com/photo-1546470427-e26264be0b0f?w=600&h=600&fit=crop",
    "Cherry Tomatoes":        "https://images.unsplash.com/photo-1561136594-7f68413baa99?w=600&h=600&fit=crop",
    "Cucumbers":              "https://images.unsplash.com/photo-1604977042946-1eecc30f269e?w=600&h=600&fit=crop",
    "Bell Pepper Red":        "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=600&h=600&fit=crop",
    "Bell Pepper Yellow":     "https://images.unsplash.com/photo-1596591868231-05e808fd131d?w=600&h=600&fit=crop",
    "Sweet Potatoes":         "https://images.unsplash.com/photo-1596097634016-b9c3b5f46571?w=600&h=600&fit=crop",
    "Potatoes":               "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&h=600&fit=crop",
    "Carrots":                "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600&h=600&fit=crop",
    "Zucchini":               "https://images.unsplash.com/photo-1583687355818-f09481e4eda4?w=600&h=600&fit=crop",
    "Eggplant":               "https://images.unsplash.com/photo-1615484477778-ca3b77940c25?w=600&h=600&fit=crop",
    "Avocado":                "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=600&h=600&fit=crop",
    "Lemons":                 "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=600&h=600&fit=crop",
    "Iceberg Lettuce":        "https://images.unsplash.com/photo-1622205313162-be1d5712a43f?w=600&h=600&fit=crop",
    "Romaine Lettuce":        "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&h=600&fit=crop",
    "Parsley":                "https://images.unsplash.com/photo-1590868309235-ea34bed7bd7f?w=600&h=600&fit=crop",
    "Cilantro":               "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600&h=600&fit=crop",
    "Mint":                   "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=600&h=600&fit=crop",
    # Dairy & Eggs
    "Milk 3%":                "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600&h=600&fit=crop",
    "Milk 1%":                "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&h=600&fit=crop",
    "Chocolate Milk":         "https://images.unsplash.com/photo-1576186726115-4d51596775d1?w=600&h=600&fit=crop",
    "Greek Yogurt":           "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600&h=600&fit=crop",
    "Natural Yogurt":         "https://images.unsplash.com/photo-1571212515416-fca88bff0136?w=600&h=600&fit=crop",
    "Cottage Cheese 5%":      "https://images.unsplash.com/photo-1631379578550-7038263db699?w=600&h=600&fit=crop",
    "Cream Cheese":           "https://images.unsplash.com/photo-1559561853-08451507cbe7?w=600&h=600&fit=crop",
    "Yellow Cheese Slices":   "https://images.unsplash.com/photo-1618164436241-4473940d1f5c?w=600&h=600&fit=crop",
    "Mozzarella Cheese":      "https://images.unsplash.com/photo-1582169296194-e4d644c48063?w=600&h=600&fit=crop",
    "Butter":                 "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600&h=600&fit=crop",
    "Whipping Cream":         "https://images.unsplash.com/photo-1587314168485-3236d6710814?w=600&h=600&fit=crop",
    "Eggs L":                 "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=600&h=600&fit=crop",
    "Eggs M":                 "https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=600&h=600&fit=crop",
    # Meat & Fish
    "Chicken Breast":         "https://images.unsplash.com/photo-1604503468506-a8da13d11d36?w=600&h=600&fit=crop",
    "Chicken Thighs":         "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=600&h=600&fit=crop",
    "Whole Chicken":          "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=600&h=600&fit=crop",
    "Ground Beef":            "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=600&h=600&fit=crop",
    "Beef Entrecote":         "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?w=600&h=600&fit=crop",
    "Beef Stew Meat":         "https://images.unsplash.com/photo-1551446591-142875a901a1?w=600&h=600&fit=crop",
    "Turkey Breast":          "https://images.unsplash.com/photo-1574672280600-4accfa5b6f98?w=600&h=600&fit=crop",
    "Turkey Shawarma":        "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=600&h=600&fit=crop",
    "Salmon Fillet":          "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600&h=600&fit=crop",
    "Tilapia Fillet":         "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=600&h=600&fit=crop",
    "Frozen Fish Fingers":    "https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?w=600&h=600&fit=crop",
    # Bakery
    "White Bread":            "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&h=600&fit=crop",
    "Whole Wheat Bread":      "https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=600&h=600&fit=crop",
    "Sourdough Bread":        "https://images.unsplash.com/photo-1585478259715-876acc5be8eb?w=600&h=600&fit=crop",
    "Pita Bread":             "https://images.unsplash.com/photo-1609167830220-7164aa360951?w=600&h=600&fit=crop",
    "Challah":                "https://images.unsplash.com/photo-1620921568790-c1cf8983a970?w=600&h=600&fit=crop",
    "Bagel":                  "https://images.unsplash.com/photo-1585478259715-876acc5be8eb?w=600&h=600&fit=crop",
    "Croissant":              "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&h=600&fit=crop",
    "Chocolate Croissant":    "https://images.unsplash.com/photo-1638185762819-d741c8c10b45?w=600&h=600&fit=crop",
    # Frozen
    "Frozen Peas":            "https://images.unsplash.com/photo-1616501268215-2d9f58b31e58?w=600&h=600&fit=crop",
    "Frozen Corn":            "https://images.unsplash.com/photo-1550828487-37cb5bb62d5b?w=600&h=600&fit=crop",
    "Frozen Fries":           "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=600&h=600&fit=crop",
    "Frozen Pizza":           "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=600&fit=crop",
    "Frozen Lasagna":         "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600&h=600&fit=crop",
    "Ice Cream Vanilla":      "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=600&h=600&fit=crop",
    "Ice Cream Chocolate":    "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&h=600&fit=crop",
    # Beverages
    "Mineral Water":          "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=600&h=600&fit=crop",
    "Sparkling Water":        "https://images.unsplash.com/photo-1560023907-5f339617ea30?w=600&h=600&fit=crop",
    "Cola":                   "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=600&h=600&fit=crop",
    "Diet Cola":              "https://images.unsplash.com/photo-1606168094336-48f205ece8f5?w=600&h=600&fit=crop",
    "Orange Juice":           "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=600&h=600&fit=crop",
    "Apple Juice":            "https://images.unsplash.com/photo-1576673442511-7e39b6545c87?w=600&h=600&fit=crop",
    "Iced Tea Lemon":         "https://images.unsplash.com/photo-1499638673689-79a0b5115d87?w=600&h=600&fit=crop",
    "Energy Drink":           "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=600&h=600&fit=crop",
    # Snacks
    "Potato Chips Classic":   "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600&h=600&fit=crop",
    "Potato Chips BBQ":       "https://images.unsplash.com/photo-1613919113640-25732ec5e61f?w=600&h=600&fit=crop",
    "Salted Peanuts":         "https://images.unsplash.com/photo-1567892320421-a25f4b5dd9e9?w=600&h=600&fit=crop",
    "Cashews Roasted":        "https://images.unsplash.com/photo-1630420958456-0bd16a4e9e2b?w=600&h=600&fit=crop",
    "Almonds Roasted":        "https://images.unsplash.com/photo-1574184864703-3487b13f0eca?w=600&h=600&fit=crop",
    "Protein Bar":            "https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=600&h=600&fit=crop",
    "Granola Bar":            "https://images.unsplash.com/photo-1627485937980-221c88ac04f9?w=600&h=600&fit=crop",
    # Pantry
    "Pasta Spaghetti":        "https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=600&h=600&fit=crop",
    "Pasta Penne":            "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=600&h=600&fit=crop",
    "Rice White":             "https://images.unsplash.com/photo-1536304993881-ff86e0c9b4da?w=600&h=600&fit=crop",
    "Rice Basmati":           "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&h=600&fit=crop",
    "Tuna Can":               "https://images.unsplash.com/photo-1618387222960-c3be5b8f75f7?w=600&h=600&fit=crop",
    "Canned Corn":            "https://images.unsplash.com/photo-1601593346740-925612772716?w=600&h=600&fit=crop",
    "Chickpeas Can":          "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=600&h=600&fit=crop",
    "Tomato Sauce":           "https://images.unsplash.com/photo-1611270629569-8b357cb88da9?w=600&h=600&fit=crop",
    "Ketchup":                "https://images.unsplash.com/photo-1553013254-e6f19ce4e11f?w=600&h=600&fit=crop",
    "Mayonnaise":             "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=600&h=600&fit=crop",
    "Olive Oil":              "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&h=600&fit=crop",
    "Sugar":                  "https://images.unsplash.com/photo-1581404417462-5e4b0e3b96ee?w=600&h=600&fit=crop",
    "Salt":                   "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=600&h=600&fit=crop",
    # Breakfast
    "Corn Flakes":            "https://images.unsplash.com/photo-1517093157656-b9eccef91cb1?w=600&h=600&fit=crop",
    "Chocolate Cereal":       "https://images.unsplash.com/photo-1588279102819-6be7a51d6827?w=600&h=600&fit=crop",
    "Oat Flakes":             "https://images.unsplash.com/photo-1614961233913-a5113a4a34ed?w=600&h=600&fit=crop",
    "Chocolate Spread":       "https://images.unsplash.com/photo-1604350834939-95a9df76a906?w=600&h=600&fit=crop",
    "Peanut Butter":          "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop",
    "Honey":                  "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=600&h=600&fit=crop",
    "Strawberry Jam":         "https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=600&h=600&fit=crop",
    # Household
    "Toilet Paper":           "https://images.unsplash.com/photo-1583947581924-860bda6a26df?w=600&h=600&fit=crop",
    "Paper Towels":           "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&h=600&fit=crop",
    "Dish Soap":              "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&h=600&fit=crop",
    "Laundry Detergent":      "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&h=600&fit=crop",
    "Fabric Softener":        "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=600&h=600&fit=crop",
    "All Purpose Cleaner":    "https://images.unsplash.com/photo-1563453392212-326f5e854473?w=600&h=600&fit=crop",
    # Personal Care
    "Shampoo":                "https://images.unsplash.com/photo-1631390163670-6fe98dac7e11?w=600&h=600&fit=crop",
    "Conditioner":            "https://images.unsplash.com/photo-1556227702-d1e4e7b5c232?w=600&h=600&fit=crop",
    "Body Wash":              "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&h=600&fit=crop",
    "Hand Soap":              "https://images.unsplash.com/photo-1584305574647-0cc949a2bb9f?w=600&h=600&fit=crop",
    "Soap Bars":              "https://images.unsplash.com/photo-1607006344380-b6775a0824a7?w=600&h=600&fit=crop",
    "Toothpaste":             "https://images.unsplash.com/photo-1612594533941-3f2e1f4c6e14?w=600&h=600&fit=crop",
    "Deodorant":              "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop",
}

# Category-level fallback images
_CATEGORY_IMAGES: dict[str, str] = {
    "Fruits & Vegetables": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=600&h=600&fit=crop",
    "Dairy & Eggs":        "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&h=600&fit=crop",
    "Meat & Fish":         "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=600&h=600&fit=crop",
    "Bakery":              "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&h=600&fit=crop",
    "Frozen":              "https://images.unsplash.com/photo-1616501268215-2d9f58b31e58?w=600&h=600&fit=crop",
    "Beverages":           "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=600&h=600&fit=crop",
    "Snacks":              "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600&h=600&fit=crop",
    "Pantry":              "https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=600&h=600&fit=crop",
    "Breakfast":           "https://images.unsplash.com/photo-1517093157656-b9eccef91cb1?w=600&h=600&fit=crop",
    "Household":           "https://images.unsplash.com/photo-1563453392212-326f5e854473?w=600&h=600&fit=crop",
    "Personal Care":       "https://images.unsplash.com/photo-1631390163670-6fe98dac7e11?w=600&h=600&fit=crop",
}


def _img(text: str, cat_name: str = "") -> str:
    # Strip value-pack suffix like " - Value Pack 2"
    base = text.split(" - Value Pack")[0].strip()
    return (
        _PRODUCT_IMAGES.get(base)
        or _CATEGORY_IMAGES.get(cat_name)
        or f"https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&h=600&fit=crop"
    )


def _ensure_product(session: Session, *, sku: str, **fields) -> Product:
    p = session.execute(select(Product).where(Product.sku == sku)).scalar_one_or_none()
    if p:
        updated = False
        for k, v in fields.items():
            if getattr(p, k, None) != v:
                setattr(p, k, v); updated = True
        if hasattr(p, "is_active") and p.is_active is False:
            p.is_active = True; updated = True
        if updated:
            session.add(p)
        return p
    p = Product(sku=sku, **fields); session.add(p); return p


def seed_products(session: Session, *, target_count: int = 180) -> list[Product]:
    cats = session.execute(select(Category)).scalars().all()
    by_name = {c.name: c for c in cats}
    if not by_name:
        raise RuntimeError("No categories found. Seed categories first.")
    rnd = random.Random(42)

    groups: list[tuple[str, list[tuple[str, str, float, str]]]] = [
    ("Fruits & Vegetables", [
        ("Apples Gala","kg",12.9,"Fresh Gala apples."),
        ("Apples Granny Smith","kg",13.9,"Green sour apples."),
        ("Bananas","kg",9.9,"Ripe bananas."),
        ("Oranges","kg",8.9,"Juicy oranges."),
        ("Mandarins","kg",10.9,"Sweet mandarins."),
        ("Tomatoes","kg",9.9,"Fresh tomatoes."),
        ("Cherry Tomatoes","500g",7.9,"Cherry tomatoes."),
        ("Cucumbers","kg",8.5,"Fresh cucumbers."),
        ("Bell Pepper Red","kg",14.9,"Red bell pepper."),
        ("Bell Pepper Yellow","kg",14.9,"Yellow bell pepper."),
        ("Sweet Potatoes","kg",11.9,"Sweet potatoes."),
        ("Potatoes","kg",6.9,"White potatoes."),
        ("Carrots","kg",6.5,"Fresh carrots."),
        ("Zucchini","kg",7.9,"Zucchini."),
        ("Eggplant","kg",8.9,"Eggplant."),
        ("Avocado","unit",6.9,"Hass avocado."),
        ("Lemons","kg",10.9,"Juicy lemons."),
        ("Iceberg Lettuce","unit",6.9,"Iceberg lettuce."),
        ("Romaine Lettuce","unit",7.9,"Romaine lettuce."),
        ("Parsley","bunch",4.9,"Fresh parsley."),
        ("Cilantro","bunch",4.9,"Fresh cilantro."),
        ("Mint","bunch",4.9,"Fresh mint."),
    ]),

    ("Dairy & Eggs", [
        ("Milk 3%","1L",6.2,"Milk 3% (1L)."),
        ("Milk 1%","1L",6.0,"Milk 1% (1L)."),
        ("Chocolate Milk","1L",6.9,"Chocolate milk."),
        ("Greek Yogurt","200g",4.9,"Greek yogurt."),
        ("Natural Yogurt","200g",3.9,"Plain yogurt."),
        ("Cottage Cheese 5%","250g",7.9,"Cottage cheese 5%."),
        ("Cream Cheese","200g",8.9,"Cream cheese."),
        ("Yellow Cheese Slices","200g",12.9,"Sliced yellow cheese."),
        ("Mozzarella Cheese","200g",11.9,"Mozzarella cheese."),
        ("Butter","200g",10.9,"Butter (200g)."),
        ("Whipping Cream","250ml",7.9,"Whipping cream."),
        ("Eggs L","12pcs",14.9,"Large eggs 12 pack."),
        ("Eggs M","12pcs",13.9,"Medium eggs 12 pack."),
    ]),

    ("Meat & Fish", [
        ("Chicken Breast","kg",39.9,"Fresh chicken breast."),
        ("Chicken Thighs","kg",34.9,"Chicken thighs."),
        ("Whole Chicken","kg",22.9,"Whole chicken."),
        ("Ground Beef","kg",59.9,"Fresh ground beef."),
        ("Beef Entrecote","kg",89.9,"Entrecote steak."),
        ("Beef Stew Meat","kg",69.9,"Beef for stew."),
        ("Turkey Breast","kg",44.9,"Turkey breast."),
        ("Turkey Shawarma","kg",52.0,"Turkey shawarma."),
        ("Salmon Fillet","kg",99.0,"Fresh salmon fillet."),
        ("Tilapia Fillet","kg",64.9,"Tilapia fillet."),
        ("Frozen Fish Fingers","400g",19.9,"Fish fingers."),
    ]),

    ("Bakery", [
        ("White Bread","750g",9.5,"White bread."),
        ("Whole Wheat Bread","750g",10.5,"Whole wheat bread."),
        ("Sourdough Bread","700g",12.9,"Sourdough bread."),
        ("Pita Bread","10pcs",8.9,"Pita bread 10 pack."),
        ("Challah","unit",14.9,"Challah."),
        ("Bagel","unit",4.9,"Fresh bagel."),
        ("Croissant","unit",6.9,"Croissant."),
        ("Chocolate Croissant","unit",7.9,"Chocolate croissant."),
    ]),

    ("Frozen", [
        ("Frozen Peas","800g",9.9,"Frozen peas."),
        ("Frozen Corn","800g",9.9,"Frozen corn."),
        ("Frozen Fries","1kg",14.9,"Frozen fries."),
        ("Frozen Pizza","unit",19.9,"Frozen pizza."),
        ("Frozen Lasagna","unit",24.9,"Frozen lasagna."),
        ("Ice Cream Vanilla","1L",24.9,"Vanilla ice cream."),
        ("Ice Cream Chocolate","1L",24.9,"Chocolate ice cream."),
    ]),

    ("Beverages", [
        ("Mineral Water","1.5L",4.5,"Mineral water."),
        ("Sparkling Water","1.5L",4.9,"Sparkling water."),
        ("Cola","1.5L",8.9,"Cola."),
        ("Diet Cola","1.5L",8.9,"Diet cola."),
        ("Orange Juice","1L",11.9,"Orange juice."),
        ("Apple Juice","1L",11.9,"Apple juice."),
        ("Iced Tea Lemon","1.5L",10.9,"Iced tea."),
        ("Energy Drink","250ml",7.9,"Energy drink."),
    ]),

    ("Snacks", [
        ("Potato Chips Classic","70g",6.5,"Potato chips."),
        ("Potato Chips BBQ","70g",6.5,"BBQ chips."),
        ("Salted Peanuts","200g",9.9,"Peanuts."),
        ("Cashews Roasted","200g",18.9,"Cashews."),
        ("Almonds Roasted","200g",18.9,"Almonds."),
        ("Protein Bar","unit",8.9,"Protein bar."),
        ("Granola Bar","unit",4.9,"Granola bar."),
    ]),

    ("Pantry", [
        ("Pasta Spaghetti","500g",6.9,"Spaghetti."),
        ("Pasta Penne","500g",6.9,"Penne pasta."),
        ("Rice White","1kg",8.9,"White rice."),
        ("Rice Basmati","1kg",11.9,"Basmati rice."),
        ("Tuna Can","160g",7.5,"Tuna can."),
        ("Canned Corn","340g",6.9,"Sweet corn."),
        ("Chickpeas Can","560g",7.9,"Chickpeas."),
        ("Tomato Sauce","500g",5.9,"Tomato sauce."),
        ("Ketchup","500g",9.9,"Ketchup."),
        ("Mayonnaise","500g",9.9,"Mayonnaise."),
        ("Olive Oil","1L",42.9,"Olive oil."),
        ("Sugar","1kg",6.9,"Sugar."),
        ("Salt","1kg",4.5,"Salt."),
    ]),

    ("Breakfast", [
        ("Corn Flakes","500g",14.9,"Corn flakes."),
        ("Chocolate Cereal","500g",16.9,"Chocolate cereal."),
        ("Oat Flakes","500g",9.9,"Oats."),
        ("Chocolate Spread","400g",17.9,"Chocolate spread."),
        ("Peanut Butter","340g",14.9,"Peanut butter."),
        ("Honey","350g",24.9,"Honey."),
        ("Strawberry Jam","340g",12.9,"Jam."),
    ]),

    ("Household", [
        ("Toilet Paper","12 rolls",29.9,"Toilet paper."),
        ("Paper Towels","6 rolls",22.9,"Paper towels."),
        ("Dish Soap","750ml",12.9,"Dish soap."),
        ("Laundry Detergent","2L",34.9,"Detergent."),
        ("Fabric Softener","2L",18.9,"Fabric softener."),
        ("All Purpose Cleaner","1L",9.9,"Cleaning spray."),
    ]),

    ("Personal Care", [
        ("Shampoo","500ml",19.9,"Shampoo."),
        ("Conditioner","500ml",19.9,"Conditioner."),
        ("Body Wash","700ml",18.9,"Body wash."),
        ("Hand Soap","500ml",7.9,"Hand soap."),
        ("Soap Bars","4pcs",9.9,"Soap bars."),
        ("Toothpaste","unit",12.9,"Toothpaste."),
        ("Deodorant","unit",16.9,"Deodorant."),
    ]),
]

    created: list[Product] = []
    i = 0
    mult = max(1, target_count // 120)
    for cat_name, items in groups:
        c = by_name.get(cat_name)
        if not c:
            continue
        aisle = (_slug(cat_name)[:1].upper() or "A")
        for base_name, unit, base_price, desc in items:
            for v in range(1, mult + 1):
                i += 1
                name = base_name if v == 1 else f"{base_name} - Value Pack {v}"
                price = Decimal(str(base_price)) + Decimal(str(rnd.choice([0,0.5,1.0,1.5])))
                old_price = (price + Decimal("2.00")) if rnd.random() < 0.25 else None
                is_org = (cat_name == "Fruits & Vegetables" and rnd.random() < 0.2)
                nutrition = None
                if cat_name in {"Beverages","Snacks","Pantry","Breakfast"} and rnd.random() < 0.8:
                    nutrition = {"calories": int(80 + rnd.random()*260), "protein_g": round(rnd.random()*12, 1)}
                sku = f"{aisle}-{_slug(base_name)[:16].upper()}-{v:02d}"
                created.append(_ensure_product(
                    session, sku=sku, name=name, category_id=c.id, price=price, old_price=old_price,
                    unit=unit, nutritional_info=nutrition, is_organic=is_org, description=desc,
                    bin_location=f"{aisle}-{i:03d}", image_url=_img(name, cat_name),
                ))
                if len(created) >= target_count:
                    session.flush(); return created

    session.flush()
    return created