from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import KnowledgeRecord, KnowledgeStore
from .decision import KnowledgeAwareDecisionEngine
from .lifecycle import KnowledgeLifecycleEngine


@dataclass(slots=True, frozen=True)
class AutonomousKnowledgeResult:
    records: tuple[dict[str, Any], ...]
    count: int
    strategy: str
    excluded: int


class AutonomousKnowledgeEngine:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.lifecycle = KnowledgeLifecycleEngine(self.store)
        self.decision = KnowledgeAwareDecisionEngine(self.store)

    def prepare(
        self,
        records: list[KnowledgeRecord],
    ) -> AutonomousKnowledgeResult:
        active = []
        excluded = 0

        for record in records:
            state = self.lifecycle.evaluate(record)

            if not state.active:
                excluded += 1
                continue

            active.append(record)

        selected = self.decision.select(active)

        return AutonomousKnowledgeResult(
            records=selected.records,
            count=selected.count,
            strategy=selected.strategy,
            excluded=excluded,
        )

    def search_and_prepare(
        self,
        query: str,
        *,
        limit: int = 10,
        verified_only: bool = True,
    ) -> AutonomousKnowledgeResult:
        from .core import KnowledgeRetriever

        retriever = KnowledgeRetriever(self.store)

        records = retriever.search(
            query,
            limit=limit,
            verified_only=verified_only,
        )

        return self.prepare(records)


autonomous = AutonomousKnowledgeEngine()


__all__ = (
    "AutonomousKnowledgeResult",
    "AutonomousKnowledgeEngine",
    "autonomous",
)
