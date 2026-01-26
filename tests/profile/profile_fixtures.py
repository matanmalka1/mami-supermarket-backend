"""Shared fixtures for profile tests."""

import pytest
from app.models import User, Address
from app.models.enums import Role

@pytest.fixture
def customer_user(session):
    """Create a test customer user."""
    session.query(User).delete()
    session.commit()
    user = User(
        email="customer@example.com",
        full_name="Test Customer",
        phone="1234567890",
        password_hash="hash",
        role=Role.CUSTOMER,
        is_active=True,
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def customer_with_addresses(session, customer_user):
    """Create a customer with multiple addresses."""
    addresses = [
        Address(
            user_id=customer_user.id,
            address_line="123 Main St",
            city="Tel Aviv",
            postal_code="12345",
            country="Israel",
            is_default=True,
        ),
        Address(
            user_id=customer_user.id,
            address_line="456 Side St",
            city="Jerusalem",
            postal_code="54321",
            country="Israel",
            is_default=False,
        ),
    ]
    for addr in addresses:
        session.add(addr)
    session.commit()
    return customer_user, addresses
