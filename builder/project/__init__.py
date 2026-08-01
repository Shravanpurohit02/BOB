from builder.project.analyzer import analyzer
from builder.project.index import index
from builder.project.model import Project
from builder.project.registry import registry

__all__ = [
    "Project",
    "analyzer",
    "index",
    "registry",
]

# Backward compatibility
indexer = index
