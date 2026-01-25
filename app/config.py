"""Configuration helpers for the Flask app."""

from __future__ import annotations
import os
from dataclasses import dataclass, field

def _env_or_default(key: str, default: str) -> str:
    return os.environ.get(key, default)

@dataclass
class AppConfig:
    DATABASE_URL: str = field(
        default_factory=lambda: _env_or_default(
            "DATABASE_URL", "postgresql+psycopg://user:pass@localhost/mami"
        )
    )
    JWT_SECRET_KEY: str = field(
        default_factory=lambda: _env_or_default("JWT_SECRET_KEY", "change-me")
    )
    DELIVERY_SOURCE_BRANCH_ID: str = field(
        default_factory=lambda: _env_or_default("DELIVERY_SOURCE_BRANCH_ID", "")
    )
    CORS_ALLOWED_ORIGINS: str = field(
        default_factory=lambda: _env_or_default("CORS_ALLOWED_ORIGINS", "*")
    )
    FRONTEND_BASE_URL: str = field(
        default_factory=lambda: _env_or_default("FRONTEND_BASE_URL", "http://localhost:5173")
    )
    BREVO_API_KEY: str = field(default_factory=lambda: _env_or_default("BREVO_API_KEY", ""))
    BREVO_TEMPLATE_ID: str = field(default_factory=lambda: _env_or_default("BREVO_TEMPLATE_ID", ""))
    SENDER_EMAIL: str = field(default_factory=lambda: _env_or_default("SENDER_EMAIL", ""))
    APP_ENV: str = field(default_factory=lambda: _env_or_default("APP_ENV", "production"))
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = field(init=False)

    def __post_init__(self) -> None:
        self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
