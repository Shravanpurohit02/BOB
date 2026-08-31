from __future__ import annotations

from dataclasses import dataclass

from .core import KnowledgeRecord, KnowledgeStore


@dataclass(slots=True, frozen=True)
class KnowledgeQuality:
    record_id: str
    confidence: float
    success_rate: float
    uses: int
    successes: int
    failures: int
    verified: bool
    promoted: bool
    eligible_for_promotion: bool
    eligible_for_retrieval: bool


class KnowledgeQualityEngine:
    MIN_SUCCESSFUL_USES = 2
    MIN_SUCCESS_RATE = 0.75

    def __init__(self, store: KnowledgeStore | None = None):
        self.store = store or KnowledgeStore()

    def evaluate(
        self,
        record: KnowledgeRecord,
    ) -> KnowledgeQuality:
        eligible_for_promotion = (
            record.verified
            and record.successes >= self.MIN_SUCCESSFUL_USES
            and record.success_rate >= self.MIN_SUCCESS_RATE
            and record.failures < record.successes
        )

        eligible_for_retrieval = (
            record.verified
            and record.confidence > 0.0
            and record.successes > record.failures
        )

        return KnowledgeQuality(
            record_id=record.id,
            confidence=record.confidence,
            success_rate=record.success_rate,
            uses=record.uses,
            successes=record.successes,
            failures=record.failures,
            verified=record.verified,
            promoted=record.promoted,
            eligible_for_promotion=eligible_for_promotion,
            eligible_for_retrieval=eligible_for_retrieval,
        )

    def evaluate_id(
        self,
        record_id: str,
    ) -> KnowledgeQuality | None:
        record = self.store.get(record_id)

        if record is None:
            return None

        return self.evaluate(record)

    def promote(
        self,
        record_id: str,
    ) -> KnowledgeRecord | None:
        record = self.store.get(record_id)

        if record is None:
            return None

        quality = self.evaluate(record)

        if not quality.eligible_for_promotion:
            return record

        record.promoted = True
        return self.store.save(record)

    def demote(
        self,
        record_id: str,
    ) -> KnowledgeRecord | None:
        record = self.store.get(record_id)

        if record is None:
            return None

        record.promoted = False
        return self.store.save(record)

    def reliable(
        self,
        record: KnowledgeRecord,
    ) -> bool:
        quality = self.evaluate(record)

        return (
            quality.eligible_for_retrieval
            and (
                quality.promoted
                or quality.eligible_for_promotion
            )
        )


quality = KnowledgeQualityEngine()


__all__ = (
    "KnowledgeQuality",
    "KnowledgeQualityEngine",
    "quality",
)
