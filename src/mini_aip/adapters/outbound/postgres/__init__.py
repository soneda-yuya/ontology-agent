"""PostgreSQL outbound adapters."""

from .activity_log import PostgresActivityLog
from .audit_sink import PostgresAuditSink
from .connection import ConnectionProvider
from .object_store import PostgresObjectStore
from .policy_store import PostgresPolicyStore
from .type_registry import PostgresTypeRegistry

__all__ = [
    "ConnectionProvider",
    "PostgresActivityLog",
    "PostgresAuditSink",
    "PostgresObjectStore",
    "PostgresPolicyStore",
    "PostgresTypeRegistry",
]
