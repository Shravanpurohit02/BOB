from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .autonomous import AutonomousKnowledgeEngine
from .core import KnowledgeRecord, KnowledgeStore
from .document import Document
from .indexer import Indexer
from .search import SearchEngine


@dataclass(slots=True, frozen=True)
class IndexedKnowledgeResult:
    documents: tuple[dict[str, Any], ...]
    count: int


class IndexedKnowledgeEngine:
    """
    Repository-document indexing bridge for BOB's persistent knowledge layer.

    This layer supplements the validated KnowledgeRecord system. It does not
    replace lifecycle, quality, decision, learning, or autonomous selection.
    """

    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.autonomous = AutonomousKnowledgeEngine(self.store)

        self.indexer = Indexer()
        self.search_engine = SearchEngine()

    def index_workspace(
        self,
        workspace: str,
    ) -> int:
        return self.indexer.build(workspace)

    def search_documents(
        self,
        query: str,
    ) -> IndexedKnowledgeResult:
        documents = self.search_engine.search(query)

        return IndexedKnowledgeResult(
            documents=tuple(
                {
                    "id": document.id,
                    "path": document.path,
                    "text": document.text,
                }
                for document in documents
            ),
            count=len(documents),
        )

    def prepare_knowledge(
        self,
        query: str,
        *,
        limit: int = 10,
        verified_only: bool = True,
    ):
        return self.autonomous.search_and_prepare(
            query,
            limit=limit,
            verified_only=verified_only,
        )


indexed = IndexedKnowledgeEngine()


__all__ = (
    "IndexedKnowledgeResult",
    "IndexedKnowledgeEngine",
    "indexed",
)
