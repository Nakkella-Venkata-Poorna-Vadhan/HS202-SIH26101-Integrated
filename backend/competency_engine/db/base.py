"""
SQLAlchemy Declarative Base and MetaData Configuration for SIH26101.
Establishes standardized naming conventions for PostgreSQL constraints and indexes.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# PostgreSQL naming conventions for predictable migration and constraint tracking
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative Base class for all SIH26101 PostgreSQL models."""
    metadata = metadata