"""PostgreSQL outbound adapters."""

from .connection import ConnectionProvider
from .object_store import PostgresObjectStore
from .policy_store import PostgresPolicyStore
from .type_registry import PostgresTypeRegistry

__all__ = [
    "ConnectionProvider",
    "PostgresObjectStore",
    "PostgresPolicyStore",
    "PostgresTypeRegistry",
]
