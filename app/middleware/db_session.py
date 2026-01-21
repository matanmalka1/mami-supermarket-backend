"""Database session management middleware."""

from __future__ import annotations

from app.extensions import db


def register_db_session_teardown(app) -> None:
    """Manage database session lifecycle for each request."""

    @app.after_request
    def commit_session(response):
        """Auto-commit successful requests."""
        if response.status_code < 400:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
        return response

    @app.teardown_appcontext
    def cleanup_session(exception=None):
        """Remove scoped_session and rollback on errors."""
        if exception is not None:
            db.session.rollback()
        db.session.remove()
