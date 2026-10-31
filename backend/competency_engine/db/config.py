"""
PostgreSQL Database Configuration Module for SIH26101.
Loads environment variables safely without initiating any database connections at import time.
Enforces least-privilege role separation:
- DATABASE_URL: Runtime application connections using sih_app_user.
- MIGRATION_DATABASE_URL: Schema management connections using sih_migrator.
- TEST_DATABASE_URL: Test runtime application connections.
- TEST_MIGRATION_DATABASE_URL: Test migration connections.
Fails clearly if required credentials are not configured.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env at project root and backend directory
CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parent.parent.parent
ROOT_DIR = BACKEND_DIR.parent

# Load environment without overriding explicitly set system environment variables
load_dotenv(ROOT_DIR / ".env", override=False)
load_dotenv(BACKEND_DIR / ".env", override=False)


def _sanitize_url(url: str | None) -> str:
    """Mask password in connection URL for safe logging/display."""
    if not url:
        return "<not set>"
    if "@" in url and "://" in url:
        prefix, rest = url.split("://", 1)
        creds, host_db = rest.split("@", 1)
        if ":" in creds:
            user, _ = creds.split(":", 1)
            return f"{prefix}://{user}:****@{host_db}"
    return url


class DatabaseSettings:
    """Database configuration container."""

    @property
    def DATABASE_URL(self) -> str:
        """Runtime application database URL (least-privilege sih_app_user)."""
        url = os.getenv("DATABASE_URL")
        if not url:
            app_user = os.getenv("DB_APP_USER", "sih_app_user")
            app_pw = os.getenv("DB_APP_PASSWORD")
            host = os.getenv("POSTGRES_HOST", "127.0.0.1")
            port = os.getenv("POSTGRES_PORT", "54329")
            db = os.getenv("DB_DEV_NAME", "sih26101_dev")
            if not app_pw:
                raise ValueError(
                    "DATABASE_URL or DB_APP_PASSWORD is not configured. "
                    "Please create a .env file based on .env.example."
                )
            url = f"postgresql+psycopg://{app_user}:{app_pw}@{host}:{port}/{db}"

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @property
    def MIGRATION_DATABASE_URL(self) -> str:
        """Schema migration database URL (schema owner sih_migrator)."""
        url = os.getenv("MIGRATION_DATABASE_URL")
        if not url:
            mig_user = os.getenv("DB_MIGRATOR_USER", "sih_migrator")
            mig_pw = os.getenv("DB_MIGRATOR_PASSWORD")
            host = os.getenv("POSTGRES_HOST", "127.0.0.1")
            port = os.getenv("POSTGRES_PORT", "54329")
            db = os.getenv("DB_DEV_NAME", "sih26101_dev")
            if not mig_pw:
                raise ValueError(
                    "MIGRATION_DATABASE_URL or DB_MIGRATOR_PASSWORD is not configured. "
                    "Schema migrations strictly require distinct migration credentials (sih_migrator) "
                    "and cannot fall back to runtime application credentials."
                )
            url = f"postgresql+psycopg://{mig_user}:{mig_pw}@{host}:{port}/{db}"

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @property
    def TEST_DATABASE_URL(self) -> str:
        """Dedicated test database URL for runtime user operations."""
        url = os.getenv("TEST_DATABASE_URL")
        if not url:
            app_user = os.getenv("DB_APP_USER", "sih_app_user")
            app_pw = os.getenv("DB_APP_PASSWORD")
            host = os.getenv("POSTGRES_HOST", "127.0.0.1")
            port = os.getenv("POSTGRES_PORT", "54329")
            db = os.getenv("DB_TEST_NAME", "sih26101_test")
            if not app_pw:
                raise ValueError(
                    "TEST_DATABASE_URL or DB_APP_PASSWORD is not configured. "
                    "Please configure .env based on .env.example."
                )
            url = f"postgresql+psycopg://{app_user}:{app_pw}@{host}:{port}/{db}"

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @property
    def TEST_MIGRATION_DATABASE_URL(self) -> str:
        """Dedicated test migration database URL for schema migrations."""
        url = os.getenv("TEST_MIGRATION_DATABASE_URL")
        if not url:
            mig_user = os.getenv("DB_MIGRATOR_USER", "sih_migrator")
            mig_pw = os.getenv("DB_MIGRATOR_PASSWORD")
            host = os.getenv("POSTGRES_HOST", "127.0.0.1")
            port = os.getenv("POSTGRES_PORT", "54329")
            db = os.getenv("DB_TEST_NAME", "sih26101_test")
            if not mig_pw:
                raise ValueError(
                    "TEST_MIGRATION_DATABASE_URL or DB_MIGRATOR_PASSWORD is not configured. "
                    "Test schema migrations strictly require distinct migration credentials (sih_migrator) "
                    "and cannot fall back to runtime application credentials."
                )
            url = f"postgresql+psycopg://{mig_user}:{mig_pw}@{host}:{port}/{db}"

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @property
    def DB_POOL_SIZE(self) -> int:
        return int(os.getenv("DB_POOL_SIZE", "10"))

    @property
    def DB_MAX_OVERFLOW(self) -> int:
        return int(os.getenv("DB_MAX_OVERFLOW", "20"))

    @property
    def DB_POOL_TIMEOUT(self) -> int:
        return int(os.getenv("DB_POOL_TIMEOUT", "30"))

    @property
    def DB_POOL_RECYCLE(self) -> int:
        return int(os.getenv("DB_POOL_RECYCLE", "1800"))

    @property
    def DB_ECHO(self) -> bool:
        return os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes")

    @property
    def ENVIRONMENT(self) -> str:
        return os.getenv("ENVIRONMENT", "development").lower()

    def get_safe_urls(self) -> dict[str, str]:
        """Return masked connection strings safe for logging and reports."""
        return {
            "DATABASE_URL": _sanitize_url(self.DATABASE_URL),
            "MIGRATION_DATABASE_URL": _sanitize_url(self.MIGRATION_DATABASE_URL),
            "TEST_DATABASE_URL": _sanitize_url(self.TEST_DATABASE_URL),
            "TEST_MIGRATION_DATABASE_URL": _sanitize_url(self.TEST_MIGRATION_DATABASE_URL),
        }


db_settings = DatabaseSettings()