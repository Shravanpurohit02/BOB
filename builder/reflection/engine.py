from __future__ import annotations

from builder.reflection.call_graph import call_graph
from builder.reflection.indexer import indexer
from builder.reflection.navigator import navigator
from builder.reflection.query import query
from builder.reflection.reference_index import reference_index
from builder.reflection.reverse_index import reverse_index
from builder.reflection.semantic_engine import semantic_engine


class ReflectionEngine:
    """
    Unified entry point for the reflection subsystem.
    """

    def index(
        self,
        workspace: str,
    ):
        return indexer.build(workspace)

    def modules(
        self,
        workspace: str,
    ):
        return query.modules(workspace)

    def symbols(
        self,
        workspace: str,
    ):
        return query.symbols(workspace)

    def search(
        self,
        workspace: str,
        text: str,
        *,
        limit: int = 25,
    ):
        return semantic_engine.search(
            workspace,
            text,
            limit=limit,
        )

    def navigate(
        self,
        workspace: str,
        text: str,
    ):
        return navigator.search(
            workspace,
            text,
        )

    def references(
        self,
        workspace: str,
    ):
        return reference_index.build(workspace)

    def reverse_index(
        self,
        workspace: str,
    ):
        return reverse_index.build(workspace)

    def call_graph(
        self,
        workspace: str,
    ):
        return call_graph.build(workspace)

    def analyze(
        self,
        workspace: str,
    ):
        self.index(workspace)

        return {
            "modules": self.modules(workspace),
            "symbols": self.symbols(workspace),
            "references": self.references(workspace),
            "reverse_index": self.reverse_index(workspace),
            "call_graph": self.call_graph(workspace),
        }


engine = ReflectionEngine()
