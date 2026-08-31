from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import KnowledgeStore
from .lifecycle import KnowledgeLifecycleEngine
from .quality import KnowledgeQualityEngine


@dataclass(slots=True, frozen=True)
class KnowledgeAuditReport:
    total: int
    active: int
    stale: int
    conflicting: int
    unreliable: int
    promoted: int
    records: tuple[dict[str, Any], ...]


class KnowledgeAuditEngine:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.lifecycle = KnowledgeLifecycleEngine(self.store)
        self.quality = KnowledgeQualityEngine(self.store)

    def audit(
        self,
        *,
        max_age_days: int | None = None,
    ) -> KnowledgeAuditReport:
        records = []
        active = 0
        stale = 0
        conflicting = 0
        unreliable = 0
        promoted = 0

        for record in self.store.all():
            lifecycle = self.lifecycle.evaluate(
                record,
                max_age_days=max_age_days,
            )
            quality = self.quality.evaluate(record)

            if lifecycle.active:
                active += 1

            if lifecycle.stale:
                stale += 1

            if lifecycle.conflicting:
                conflicting += 1

            if not quality.eligible_for_retrieval:
                unreliable += 1

            if record.promoted:
                promoted += 1

            records.append(
                {
                    "id": record.id,
                    "title": record.title,
                    "category": record.category,
                    "confidence": record.confidence,
                    "success_rate": record.success_rate,
                    "uses": record.uses,
                    "successes": record.successes,
                    "failures": record.failures,
                    "promoted": record.promoted,
                    "verified": record.verified,
                    "active": lifecycle.active,
                    "stale": lifecycle.stale,
                    "conflicting": lifecycle.conflicting,
                    "reliable": quality.eligible_for_retrieval,
                    "reason": lifecycle.reason,
                }
            )

        return KnowledgeAuditReport(
            total=len(records),
            active=active,
            stale=stale,
            conflicting=conflicting,
            unreliable=unreliable,
            promoted=promoted,
            records=tuple(records),
        )

    def health(
        self,
        *,
        max_age_days: int | None = None,
    ) -> dict[str, Any]:
        report = self.audit(
            max_age_days=max_age_days,
        )

        return {
            "total": report.total,
            "active": report.active,
            "stale": report.stale,
            "conflicting": report.conflicting,
            "unreliable": report.unreliable,
            "promoted": report.promoted,
            "healthy": (
                report.total > 0
                and report.conflicting == 0
                and report.stale == 0
            ),
        }


audit = KnowledgeAuditEngine()


__all__ = (
    "KnowledgeAuditReport",
    "KnowledgeAuditEngine",
    "audit",
)
