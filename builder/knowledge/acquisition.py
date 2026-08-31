from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import KnowledgeLearningEngine, KnowledgeRecord, KnowledgeStore


@dataclass(slots=True, frozen=True)
class AcquisitionResult:
    acquired: bool
    record_id: str | None
    source: str
    validator: str
    reason: str
    record: KnowledgeRecord | None = None


class AutonomousKnowledgeAcquisition:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.learning = KnowledgeLearningEngine(self.store)

    def acquire(
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
    ) -> AcquisitionResult:
        if not passed:
            return AcquisitionResult(
                acquired=False,
                record_id=None,
                source=source,
                validator=validator,
                reason="Validation did not pass.",
            )

        record = self.learning.learn_from_validated_result(
            category=category,
            title=title,
            content=content,
            source=source,
            validator=validator,
            passed=True,
            workspace=workspace,
            tags=tags,
            language=language,
            framework=framework,
            version=version,
        )

        return AcquisitionResult(
            acquired=True,
            record_id=record.id,
            source=source,
            validator=validator,
            reason="Validated execution knowledge acquired.",
            record=record,
        )

    def acquire_from_validation(
        self,
        *,
        category: str,
        title: str,
        content: str,
        validation: dict[str, Any],
        source: str,
        validator: str,
        workspace: str = "",
        tags: list[str] | None = None,
        language: str = "",
        framework: str = "",
        version: str = "",
    ) -> AcquisitionResult:
        passed = (
            bool(validation.get("failed", 0) == 0)
            and bool(validation.get("passed", True))
        )

        return self.acquire(
            category=category,
            title=title,
            content=content,
            source=source,
            validator=validator,
            passed=passed,
            workspace=workspace,
            tags=tags,
            language=language,
            framework=framework,
            version=version,
        )


acquisition = AutonomousKnowledgeAcquisition()


__all__ = (
    "AcquisitionResult",
    "AutonomousKnowledgeAcquisition",
    "acquisition",
)
