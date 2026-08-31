from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from builder.config import settings


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(category: str, title: str, content: str) -> str:
    value = f"{category}\n{title}\n{content}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


@dataclass(slots=True)
class KnowledgeEvidence:
    source: str = ""
    source_type: str = ""
    reference: str = ""
    validator: str = ""
    status: str = "unverified"
    message: str = ""
    timestamp: str = field(default_factory=_now)


@dataclass(slots=True)
class KnowledgeRecord:
    id: str
    category: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    language: str = ""
    framework: str = ""
    version: str = ""
    confidence: float = 0.0
    evidence: list[KnowledgeEvidence] = field(default_factory=list)
    provenance: str = ""
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    uses: int = 0
    successes: int = 0
    failures: int = 0
    promoted: bool = False

    @property
    def verified(self) -> bool:
        return any(
            evidence.status == "verified"
            for evidence in self.evidence
        )

    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        if total == 0:
            return 0.0
        return self.successes / total


class KnowledgeStore:
    def __init__(self):
        self.root = (
            settings.resolve_memory_directory()
            / "knowledge"
        )
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _file(self, record_id: str) -> Path:
        return self.root / f"{record_id}.json"

    def save(self, record: KnowledgeRecord) -> KnowledgeRecord:
        record.updated_at = _now()

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self._file(record.id)
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(
                asdict(record),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        temporary.replace(target)

        return record

    def get(self, record_id: str) -> KnowledgeRecord | None:
        target = self._file(record_id)

        if not target.exists():
            return None

        try:
            data = json.loads(
                target.read_text(
                    encoding="utf-8",
                )
            )
        except (OSError, ValueError):
            return None

        evidence = [
            KnowledgeEvidence(**item)
            for item in data.pop("evidence", [])
        ]

        return KnowledgeRecord(
            **data,
            evidence=evidence,
        )

    def all(self) -> list[KnowledgeRecord]:
        records = []

        for target in sorted(self.root.glob("*.json")):
            record = self.get(target.stem)

            if record is not None:
                records.append(record)

        return records

    def delete(self, record_id: str) -> bool:
        target = self._file(record_id)

        if not target.exists():
            return False

        target.unlink()
        return True


class KnowledgeRetriever:
    def __init__(self, store: KnowledgeStore):
        self.store = store

    def search(
        self,
        query: str,
        *,
        category: str | None = None,
        language: str | None = None,
        limit: int = 10,
        verified_only: bool = False,
    ) -> list[KnowledgeRecord]:
        tokens = {
            token
            for token in query.lower().split()
            if token
        }

        scored = []

        for record in self.store.all():
            if category and record.category != category:
                continue

            if language and record.language.lower() != language.lower():
                continue

            if verified_only and not record.verified:
                continue

            haystack = " ".join(
                (
                    record.title,
                    record.content,
                    record.category,
                    record.language,
                    record.framework,
                    record.version,
                    " ".join(record.tags),
                )
            ).lower()

            score = sum(
                1
                for token in tokens
                if token in haystack
            )

            if score:
                scored.append(
                    (
                        score,
                        record.confidence,
                        record.success_rate,
                        record,
                    )
                )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2],
            ),
            reverse=True,
        )

        return [
            item[3]
            for item in scored[:max(0, limit)]
        ]


class KnowledgeLearningEngine:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.retriever = KnowledgeRetriever(
            self.store
        )

    def record(
        self,
        *,
        category: str,
        title: str,
        content: str,
        tags: list[str] | None = None,
        language: str = "",
        framework: str = "",
        version: str = "",
        provenance: str = "",
        evidence: list[KnowledgeEvidence] | None = None,
        confidence: float = 0.0,
    ) -> KnowledgeRecord:
        record = KnowledgeRecord(
            id=_stable_id(
                category,
                title,
                content,
            ),
            category=category,
            title=title,
            content=content,
            tags=list(tags or []),
            language=language,
            framework=framework,
            version=version,
            provenance=provenance,
            evidence=list(evidence or []),
            confidence=max(
                0.0,
                min(1.0, float(confidence)),
            ),
        )

        existing = self.store.get(record.id)

        if existing is not None:
            existing.tags = sorted(
                set(existing.tags)
                | set(record.tags)
            )

            existing.evidence.extend(
                record.evidence
            )

            existing.confidence = max(
                existing.confidence,
                record.confidence,
            )

            if record.provenance:
                existing.provenance = record.provenance

            return self.store.save(existing)

        return self.store.save(record)

    def record_success(
        self,
        record_id: str,
        *,
        evidence: KnowledgeEvidence | None = None,
    ) -> KnowledgeRecord | None:
        record = self.store.get(record_id)

        if record is None:
            return None

        record.uses += 1
        record.successes += 1

        if evidence is not None:
            evidence.status = "verified"
            record.evidence.append(evidence)

        record.confidence = min(
            1.0,
            max(
                record.confidence,
                min(
                    1.0,
                    record.successes
                    / max(
                        1,
                        record.successes
                        + record.failures,
                    ),
                ),
            ),
        )

        if (
            record.successes >= 2
            and record.verified
        ):
            record.promoted = True

        return self.store.save(record)

    def record_failure(
        self,
        record_id: str,
        *,
        evidence: KnowledgeEvidence | None = None,
    ) -> KnowledgeRecord | None:
        record = self.store.get(record_id)

        if record is None:
            return None

        record.uses += 1
        record.failures += 1

        if evidence is not None:
            evidence.status = "failed"
            record.evidence.append(evidence)

        return self.store.save(record)

    def learn_from_validated_result(
        self,
        *,
        category: str,
        title: str,
        content: str,
        source: str,
        validator: str,
        passed: bool,
        workspace: str = "",
        tags: list[str] | None = None,
        language: str = "",
        framework: str = "",
        version: str = "",
    ) -> KnowledgeRecord:
        evidence = KnowledgeEvidence(
            source=source,
            source_type="validated_execution",
            reference=workspace,
            validator=validator,
            status="verified" if passed else "failed",
            message=(
                "Validation passed."
                if passed
                else "Validation failed."
            ),
        )

        record = self.record(
            category=category,
            title=title,
            content=content,
            tags=tags,
            language=language,
            framework=framework,
            version=version,
            provenance=source,
            evidence=[evidence],
            confidence=1.0 if passed else 0.0,
        )

        if passed:
            return self.record_success(
                record.id,
                evidence=evidence,
            ) or record

        return self.record_failure(
            record.id,
            evidence=evidence,
        ) or record

    def search(
        self,
        query: str,
        **kwargs: Any,
    ) -> list[KnowledgeRecord]:
        return self.retriever.search(
            query,
            **kwargs,
        )


store = KnowledgeStore()
retriever = KnowledgeRetriever(store)
learning = KnowledgeLearningEngine(store)

__all__ = (
    "KnowledgeEvidence",
    "KnowledgeRecord",
    "KnowledgeStore",
    "KnowledgeRetriever",
    "KnowledgeLearningEngine",
    "store",
    "retriever",
    "learning",
)
