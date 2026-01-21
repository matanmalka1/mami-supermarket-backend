# seed/utils.py
from __future__ import annotations
from sqlalchemy.orm import Session

def commit_or_rollback(session: Session) -> None:
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise