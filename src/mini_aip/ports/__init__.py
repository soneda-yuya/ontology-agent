"""Ports — interfaces the core requires from the outside world (driven side).

Adapters in ``mini_aip.adapters.outbound`` implement these. The core depends
only on these Protocols, never on concrete technology (hexagonal architecture).
"""

from .activity_log import ActivityLogPort
from .audit_sink import AuditSinkPort
from .object_store import ObjectStorePort
from .policy_store import PolicyStorePort
from .type_registry import TypeRegistryPort

__all__ = [
    "ActivityLogPort",
    "AuditSinkPort",
    "ObjectStorePort",
    "PolicyStorePort",
    "TypeRegistryPort",
]
