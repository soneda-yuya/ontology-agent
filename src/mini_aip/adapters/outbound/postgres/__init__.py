"""PostgreSQL outbound adapters."""

from .connection import ConnectionProvider
from .object_store import PostgresObjectStore
from .type_registry import PostgresTypeRegistry

__all__ = ["ConnectionProvider", "PostgresObjectStore", "PostgresTypeRegistry"]
