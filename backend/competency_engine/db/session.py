"""
Database Engine and Session Lifecycle Management for SIH26101.
Ensures connection pooling, connection health verification, and explicit transaction management.
No connections are created at module import time.
"""

from __future__ import annotations

from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session

from competency_engine.db.config import db_settings

_ENGINES: dict[str, Engine] = {}
_SESSION_FACTORIES: dict[str, sessionmaker[Session]] = {}


def get_engine(db_url: str | None = None, echo: bool | None = None) -> Engine:
    """
    Get or create a SQLAlchemy Engine with connection pooling and health checks.
    Engine creation is lazy: no network connection occurs until checkout.
    """
    url = db_url or db_settings.DATABASE_URL
    effective_echo = echo if echo is not None else db_settings.DB_ECHO

    cache_key = f"{url}_echo={effective_echo}"
    if cache_key not in _ENGINES:
        _ENGINES[cache_key] = create_engine(
            url,
            pool_pre_ping=True,  # Proactively tests connection liveness before checkout
            pool_size=db_settings.DB_POOL_SIZE,
            max_overflow=db_settings.DB_MAX_OVERFLOW,
            pool_timeout=db_settings.DB_POOL_TIMEOUT,
            pool_recycle=db_settings.DB_POOL_RECYCLE,
            echo=effective_echo,
            future=True,
        )
    return _ENGINES[cache_key]


def get_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Get or create a session factory bound to the specified engine."""
    eng = engine or get_engine()
    eng_id = str(id(eng))
    if eng_id not in _SESSION_FACTORIES:
        _SESSION_FACTORIES[eng_id] = sessionmaker(
            bind=eng,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SESSION_FACTORIES[eng_id]


def get_db(db_url: str | None = None) -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a transactional database session for business operations.
    Commits on normal exit, rolls back on exception, and guarantees session closure.
    """
    engine = get_engine(db_url)
    session_factory = get_session_factory(engine)
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_audit_db(db_url: str | None = None) -> Generator[Session, None, None]:
    """
    Autonomous database session dedicated to application audit log writes.
    Isolates compliance auditing from user transaction rollbacks.

    Role & Trust Boundary Architecture:
    - Connects using the runtime application role (sih_app_user).
    - Under the Phase 1 least-privilege model, sih_app_user is granted SELECT and INSERT
      on application_audit_logs, while UPDATE, DELETE, and TRUNCATE are revoked.
    - Provides TRANSACTION-LEVEL isolation (an autonomous transaction boundary via a
      distinct connection from the pool), ensuring audit records persist even if the
      enclosing business transaction encounters an error and rolls back.
    - Note: It does NOT use a separate database user role.
    """
    engine = get_engine(db_url)
    session_factory = get_session_factory(engine)
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Context managers for direct procedural / background use outside FastAPI dependency injection
db_session_scope = contextmanager(get_db)
audit_session_scope = contextmanager(get_audit_db)


def check_db_health(engine: Engine | None = None) -> bool:
    """
    Actively checks PostgreSQL connection health via a lightweight SELECT 1 probe.
    Returns True if healthy, False otherwise.
    """
    eng = engine or get_engine()
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
