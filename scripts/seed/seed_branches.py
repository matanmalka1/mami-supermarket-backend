# seed/seed_branches.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.branch import Branch  


def _ensure_branch(session: Session, *, name: str, address: str) -> Branch:
    """
    Idempotent insert/update by unique name.
    - If exists: update address if changed
    - If soft-deleted: reactivate
    """
    branch = session.execute(
        select(Branch).where(Branch.name == name)
    ).scalar_one_or_none()

    if branch:
        updated = False

        if hasattr(branch, "is_active") and branch.is_active is False:
            branch.is_active = True
            updated = True

        if branch.address != address:
            branch.address = address
            updated = True

        if updated:
            session.add(branch)

        return branch

    branch = Branch(name=name, address=address)
    session.add(branch)
    return branch


def seed_branches(session: Session) -> list[Branch]:
    """
    Creates a realistic initial set of branches.
    You can expand/replace addresses as needed.
    """
    branches_data = [
        {"name": "Mami Supermarket - Tel Aviv", "address": "Dizengoff 123, Tel Aviv-Yafo, Israel"},
        {"name": "Mami Supermarket - Jerusalem", "address": "HaNevi'im 25, Jerusalem, Israel"},
        {"name": "Mami Supermarket - Haifa", "address": "HaNasi 10, Haifa, Israel"},
        {"name": "Mami Supermarket - Rishon LeZion", "address": "Rothschild Blvd 15, Rishon LeZion, Israel"},
        {"name": "Mami Supermarket - Be'er Sheva", "address": "HaAtzmaut 8, Be'er Sheva, Israel"},
    ]

    created_or_existing: list[Branch] = []
    for item in branches_data:
        created_or_existing.append(
            _ensure_branch(session, name=item["name"], address=item["address"])
        )

    session.flush()  
    return created_or_existing