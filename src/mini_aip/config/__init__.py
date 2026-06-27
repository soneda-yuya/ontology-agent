"""Configuration and composition root."""

from .container import build_ontology_service
from .settings import Settings

__all__ = ["Settings", "build_ontology_service"]
