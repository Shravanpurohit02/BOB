from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .autonomous import AutonomousKnowledgeEngine
from .core import KnowledgeRecord, KnowledgeStore


@dataclass(slots=True, frozen=True)
class KnowledgeReplanningContext:
    records: tuple[dict[str, Any], ...]
    count: int
    strategy: str
    excluded: int


class KnowledgeReplanningEngine:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.autonomous = AutonomousKnowledgeEngine(self.store)

    def prepare(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> KnowledgeReplanningContext:
        result = self.autonomous.search_and_prepare(
            query,
            limit=limit,
            verified_only=True,
        )

        return KnowledgeReplanningContext(
            records=result.records,
            count=result.count,
            strategy=result.strategy,
            excluded=result.excluded,
        )

    def context(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        prepared = self.prepare(
            query,
            limit=limit,
        )

        return list(prepared.records)

    def enrich(
        self,
        objective: str,
        *,
        query: str | None = None,
        limit: int = 5,
    ) -> dict[str, Any]:
        search_query = query or objective

        prepared = self.prepare(
            search_query,
            limit=limit,
        )

        return {
            "objective": objective,
            "knowledge": list(prepared.records),
            "knowledge_count": prepared.count,
            "knowledge_strategy": prepared.strategy,
            "knowledge_excluded": prepared.excluded,
        }


replanning = KnowledgeReplanningEngine()


__all__ = (
    "KnowledgeReplanningContext",
    "KnowledgeReplanningEngine",
    "replanning",
)
