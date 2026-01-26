# seed/seed_users.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User  
from app.models.enums import Role


def _ensure_user(
    session: Session,
    *,
    email: str,
    full_name: str,
    password_hash: str,
    role: Role,
    default_branch_id=None,
) -> User:
    user = session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if user:
        updated = False

        if hasattr(user, "is_active") and user.is_active is False:
            user.is_active = True
            updated = True

        if user.full_name != full_name:
            user.full_name = full_name
            updated = True

        if user.role != role:
            user.role = role
            updated = True

        if default_branch_id and user.default_branch_id != default_branch_id:
            user.default_branch_id = default_branch_id
            updated = True

        if updated:
            session.add(user)

        return user

    user = User(
        email=email,
        full_name=full_name,
        password_hash=password_hash,
        role=role,
        default_branch_id=default_branch_id,
    )
    session.add(user)
    return user


def seed_users(session: Session, *, default_branch_id, password: str = "Mami2026!") -> list[User]:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    users_data = [
        # Customers
        {
            "email": "noam.levi@example.com",
            "full_name": "Noam Levi",
            "role": Role.CUSTOMER,
        },
        {
            "email": "yael.cohen@example.com",
            "full_name": "Yael Cohen",
            "role": Role.CUSTOMER,
        },
        {
            "email": "itamari.ben@example.com",
            "full_name": "Itamari Ben-David",
            "role": Role.CUSTOMER,
        },

        # Staff
        {
            "email": "employee1@mami.local",
            "full_name": "Mami Employee",
            "role": Role.EMPLOYEE,
        },
        {
            "email": "manager@mami.local",
            "full_name": "Mami Manager",
            "role": Role.MANAGER,
        },
        {
            "email": "admin@mami.local",
            "full_name": "Mami Admin",
            "role": Role.ADMIN,
        },
    ]

    created: list[User] = []

    for item in users_data:
        created.append(
            _ensure_user(
                session,
                email=item["email"],
                full_name=item["full_name"],
                password_hash=pwd_context.hash(password),
                role=item["role"],
                default_branch_id=default_branch_id,
            )
        )

    session.flush()
    return created
