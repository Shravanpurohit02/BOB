from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import KnowledgeRecord, KnowledgeStore
from .quality import KnowledgeQualityEngine


@dataclass(slots=True, frozen=True)
class KnowledgeDecision:
    records: tuple[dict[str, Any], ...]
    count: int
    reliable: bool
    strategy: str


class KnowledgeAwareDecisionEngine:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.quality = KnowledgeQualityEngine(self.store)

    def select(
        self,
        records: list[KnowledgeRecord],
    ) -> KnowledgeDecision:
        selected = []

        for record in records:
            if not self.quality.reliable(record):
                continue

            selected.append(
                {
                    "id": record.id,
                    "title": record.title,
                    "content": record.content,
                    "category": record.category,
                    "confidence": record.confidence,
                    "success_rate": record.success_rate,
                    "promoted": record.promoted,
                }
            )

        strategy = (
            "knowledge_guided_repair"
            if selected
            else "standard_repair"
        )

        return KnowledgeDecision(
            records=tuple(selected),
            count=len(selected),
            reliable=bool(selected),
            strategy=strategy,
        )


decision = KnowledgeAwareDecisionEngine()


__all__ = (
    "KnowledgeDecision",
    "KnowledgeAwareDecisionEngine",
    "decision",
)
