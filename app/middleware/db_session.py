from __future__ import annotations

from app.extensions import db

def register_db_session_teardown(app) -> None:
    @app.teardown_appcontext
    def cleanup_session(exception=None):
        if exception is not None:
            db.session.rollback()
        db.session.remove()
