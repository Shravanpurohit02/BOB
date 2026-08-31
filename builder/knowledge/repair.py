from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .replanning import KnowledgeReplanningEngine
from .core import KnowledgeStore


@dataclass(slots=True, frozen=True)
class KnowledgeRepairDecision:
    strategy: str
    knowledge_count: int
    knowledge: tuple[dict[str, Any], ...]
    reason: str


class KnowledgeRepairSelector:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.replanning = KnowledgeReplanningEngine(self.store)

    def select(
        self,
        objective: str,
        *,
        query: str | None = None,
        limit: int = 5,
    ) -> KnowledgeRepairDecision:
        context = self.replanning.enrich(
            objective,
            query=query,
            limit=limit,
        )

        knowledge = tuple(
            context["knowledge"]
        )

        if knowledge:
            return KnowledgeRepairDecision(
                strategy="knowledge_guided_repair",
                knowledge_count=len(knowledge),
                knowledge=knowledge,
                reason=(
                    "Reliable learned knowledge is available "
                    "for the repair objective."
                ),
            )

        return KnowledgeRepairDecision(
            strategy="standard_repair",
            knowledge_count=0,
            knowledge=(),
            reason=(
                "No reliable learned knowledge is available "
                "for the repair objective."
            ),
        )


repair_selector = KnowledgeRepairSelector()


__all__ = (
    "KnowledgeRepairDecision",
    "KnowledgeRepairSelector",
    "repair_selector",
)
