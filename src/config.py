"""Configuration helpers for the Flask app."""

from dataclasses import dataclass


@dataclass
class AppConfig:
    DATABASE_URL: str = "postgresql+psycopg://user:pass@localhost/mami"
    JWT_SECRET_KEY: str = "change-me"
    DELIVERY_SOURCE_BRANCH_ID: str = ""
