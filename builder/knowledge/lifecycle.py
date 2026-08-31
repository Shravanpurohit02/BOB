from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .core import KnowledgeRecord, KnowledgeStore


def _parse_timestamp(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return None


@dataclass(slots=True, frozen=True)
class KnowledgeLifecycle:
    record_id: str
    stale: bool
    conflicting: bool
    superseded: bool
    active: bool
    reason: str


class KnowledgeLifecycleEngine:
    DEFAULT_MAX_AGE_DAYS = 180

    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()

    def is_stale(
        self,
        record: KnowledgeRecord,
        *,
        max_age_days: int | None = None,
    ) -> bool:
        maximum = (
            self.DEFAULT_MAX_AGE_DAYS
            if max_age_days is None
            else max(0, int(max_age_days))
        )

        updated = _parse_timestamp(record.updated_at)

        if updated is None:
            return True

        now = datetime.now(timezone.utc)

        if updated.tzinfo is None:
            updated = updated.replace(
                tzinfo=timezone.utc
            )

        age = now - updated

        return age.total_seconds() > (
            maximum * 86400
        )

    def find_conflicts(
        self,
        record: KnowledgeRecord,
    ) -> list[KnowledgeRecord]:
        conflicts = []

        for candidate in self.store.all():
            if candidate.id == record.id:
                continue

            if candidate.category != record.category:
                continue

            if candidate.language != record.language:
                continue

            if (
                candidate.title.lower()
                == record.title.lower()
            ):
                if (
                    candidate.content.strip().lower()
                    != record.content.strip().lower()
                ):
                    conflicts.append(candidate)

        return conflicts

    def evaluate(
        self,
        record: KnowledgeRecord,
        *,
        max_age_days: int | None = None,
    ) -> KnowledgeLifecycle:
        stale = self.is_stale(
            record,
            max_age_days=max_age_days,
        )

        conflicts = self.find_conflicts(record)
        conflicting = bool(conflicts)

        superseded = (
            stale
            or conflicting
        )

        active = (
            not superseded
            and record.confidence > 0.0
            and record.failures <= record.successes
        )

        if conflicting:
            reason = "conflicting knowledge exists"
        elif stale:
            reason = "knowledge is stale"
        elif not active:
            reason = "knowledge quality is insufficient"
        else:
            reason = "knowledge is active"

        return KnowledgeLifecycle(
            record_id=record.id,
            stale=stale,
            conflicting=conflicting,
            superseded=superseded,
            active=active,
            reason=reason,
        )

    def supersede(
        self,
        record_id: str,
    ) -> KnowledgeRecord | None:
        record = self.store.get(record_id)

        if record is None:
            return None

        record.promoted = False
        record.confidence = min(
            record.confidence,
            0.25,
        )

        return self.store.save(record)


lifecycle = KnowledgeLifecycleEngine()


__all__ = (
    "KnowledgeLifecycle",
    "KnowledgeLifecycleEngine",
    "lifecycle",
)
