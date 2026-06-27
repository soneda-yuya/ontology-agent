"""Ports — interfaces the core requires from the outside world (driven side).

Adapters in ``mini_aip.adapters.outbound`` implement these. The core depends
only on these Protocols, never on concrete technology (hexagonal architecture).
"""

from .object_store import ObjectStorePort
from .policy_store import PolicyStorePort
from .type_registry import TypeRegistryPort

__all__ = ["ObjectStorePort", "PolicyStorePort", "TypeRegistryPort"]
