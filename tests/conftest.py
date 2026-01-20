import sys
import uuid
from pathlib import Path
from datetime import time

import pytest
import sys
from flask_jwt_extended import create_access_token

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.config import AppConfig
from app.extensions import db
from app.models import Base, Branch, Category, DeliverySlot, Inventory, Product, User
from app.models.enums import Role


@pytest.fixture(scope="session")
def test_app():
    warehouse_id = uuid.uuid4()
    cfg = AppConfig(
        DATABASE_URL="sqlite:///:memory:",
        JWT_SECRET_KEY="test",
        DELIVERY_SOURCE_BRANCH_ID=str(warehouse_id),
    )
    app = create_app(cfg)
    app.config["TESTING"] = True
    with app.app_context():
        Base.metadata.create_all(bind=db.engine)
        # Seed warehouse branch + slot
        branch = Branch(id=warehouse_id, name="Warehouse", address="Nowhere 1")
        db.session.add(branch)
        slot = DeliverySlot(
            branch_id=warehouse_id,
            day_of_week=0,
            start_time=time(6, 0),
            end_time=time(8, 0),
        )
        db.session.add(slot)
        db.session.commit()
    yield app
    with app.app_context():
        Base.metadata.drop_all(bind=db.engine)


@pytest.fixture
def session(test_app):
    with test_app.app_context():
        # Fresh DB per test
        Base.metadata.drop_all(bind=db.engine)
        Base.metadata.create_all(bind=db.engine)
        warehouse_id = uuid.UUID(test_app.config["DELIVERY_SOURCE_BRANCH_ID"])
        branch = Branch(id=warehouse_id, name="Warehouse", address="Nowhere 1")
        db.session.add(branch)
        slot = DeliverySlot(
            branch_id=warehouse_id,
            day_of_week=0,
            start_time=time(6, 0),
            end_time=time(8, 0),
        )
        db.session.add(slot)
        db.session.commit()
        yield db.session
        db.session.rollback()


@pytest.fixture
def users(session):
    session.query(User).delete()
    session.commit()
    created = []
    for i in range(2):
        user = User(
            email=f"u{i}@example.com",
            full_name=f"User {i}",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        session.add(user)
        created.append(user)
    session.commit()
    return created


@pytest.fixture
def product_with_inventory(session, test_app):
    warehouse_id = uuid.UUID(test_app.config["DELIVERY_SOURCE_BRANCH_ID"])
    session.query(Branch).filter(Branch.name == "Pickup").delete()
    other_branch = Branch(name="Pickup", address="Street 2")
    session.add(other_branch)
    category = Category(name="Dairy")
    session.add(category)
    session.flush()
    product = Product(name="Milk", sku="SKU1", price="10.00", category_id=category.id)
    session.add(product)
    session.flush()
    inv = Inventory(
        product_id=product.id,
        branch_id=warehouse_id,
        available_quantity=1,
        reserved_quantity=0,
    )
    session.add(inv)
    session.commit()
    return product, inv, other_branch


@pytest.fixture
def auth_header(test_app):
    def _build(user):
        with test_app.app_context():
            token = create_access_token(identity=str(user.id), additional_claims={"role": user.role.value})
        return {"Authorization": f"Bearer {token}"}

    return _build
