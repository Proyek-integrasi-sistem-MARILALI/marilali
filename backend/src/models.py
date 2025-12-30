from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# PostgreSQL naming conventions for constraints and indexes
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

# Base class for all ORM models - must be defined here to avoid circular imports
# All service models should inherit from this Base
Base = declarative_base(metadata=MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION))
