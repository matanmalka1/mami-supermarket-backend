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
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = field(init=False)

    def __post_init__(self) -> None:
        self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
