from __future__ import annotations

from dataclasses import dataclass
import re

from .core import KnowledgeLearningEngine, KnowledgeRecord, KnowledgeStore


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", value.lower())
        if len(token) > 2
    }


@dataclass(slots=True, frozen=True)
class ConsolidationResult:
    primary_id: str
    merged_ids: tuple[str, ...]
    changed: bool


class KnowledgeConsolidationEngine:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.learning = KnowledgeLearningEngine(self.store)

    def similarity(
        self,
        left: KnowledgeRecord,
        right: KnowledgeRecord,
    ) -> float:
        if left.category != right.category:
            return 0.0

        left_tokens = _tokens(
            left.title + " " + left.content
        )
        right_tokens = _tokens(
            right.title + " " + right.content
        )

        if not left_tokens or not right_tokens:
            return 0.0

        intersection = left_tokens & right_tokens
        union = left_tokens | right_tokens

        return len(intersection) / len(union)

    def find_duplicates(
        self,
        record: KnowledgeRecord,
        *,
        threshold: float = 0.70,
    ) -> list[KnowledgeRecord]:
        matches = []

        for candidate in self.store.all():
            if candidate.id == record.id:
                continue

            if self.similarity(record, candidate) >= threshold:
                matches.append(candidate)

        return matches

    def consolidate(
        self,
        record: KnowledgeRecord,
        *,
        threshold: float = 0.70,
    ) -> ConsolidationResult:
        persisted = self.store.get(record.id)

        if persisted is not None:
            record = persisted

        duplicates = self.find_duplicates(
            record,
            threshold=threshold,
        )

        if not duplicates:
            return ConsolidationResult(
                primary_id=record.id,
                merged_ids=(),
                changed=False,
            )

        candidates = [record] + duplicates

        primary = max(
            candidates,
            key=lambda item: (
                int(item.promoted),
                item.successes,
                item.confidence,
                item.success_rate,
                item.uses,
            ),
        )

        merged_ids = []

        for candidate in candidates:
            if candidate.id == primary.id:
                continue

            primary.tags = sorted(
                set(primary.tags)
                | set(candidate.tags)
            )

            primary.evidence.extend(
                candidate.evidence
            )

            primary.uses += candidate.uses
            primary.successes += candidate.successes
            primary.failures += candidate.failures

            primary.confidence = max(
                primary.confidence,
                candidate.confidence,
            )

            if candidate.provenance:
                if primary.provenance:
                    if candidate.provenance not in primary.provenance:
                        primary.provenance += (
                            "; " + candidate.provenance
                        )
                else:
                    primary.provenance = candidate.provenance

            primary.promoted = (
                primary.promoted
                or candidate.promoted
            )

            merged_ids.append(candidate.id)

        self.store.save(primary)

        for record_id in merged_ids:
            self.store.delete(record_id)

        return ConsolidationResult(
            primary_id=primary.id,
            merged_ids=tuple(merged_ids),
            changed=True,
        )


consolidation = KnowledgeConsolidationEngine()


__all__ = (
    "ConsolidationResult",
    "KnowledgeConsolidationEngine",
    "consolidation",
)
