from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeRecord:
    record_id: str
    asset_id: str
    lesson: str
    outcome: str
    score: float
    reusable: bool = False
    metadata: dict | None = None

    def __post_init__(self):
        if not self.record_id:
            raise ValueError("record_id must not be empty")
        if not self.asset_id:
            raise ValueError("asset_id must not be empty")
        if not self.lesson:
            raise ValueError("lesson must not be empty")
        if not self.outcome:
            raise ValueError("outcome must not be empty")
        if not 0.0 <= self.score <= 10.0:
            raise ValueError(
                "score must be between 0.0 and 10.0"
            )

        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "asset_id": self.asset_id,
            "lesson": self.lesson,
            "outcome": self.outcome,
            "score": self.score,
            "reusable": self.reusable,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class KnowledgeIntegrationResult:
    records: tuple[KnowledgeRecord, ...]
    integrated: bool
    reusable_assets: tuple[str, ...]
    failed_assets: tuple[str, ...]
    lessons: tuple[str, ...]
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "records": [
                record.to_dict()
                for record in self.records
            ],
            "integrated": self.integrated,
            "reusable_assets": list(
                self.reusable_assets
            ),
            "failed_assets": list(
                self.failed_assets
            ),
            "lessons": list(self.lessons),
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryKnowledgeIntegrator:
    """
    Converts outcome-learning information into deterministic
    knowledge records and identifies assets whose prior outcomes
    can influence future construction.

    The integrator is intentionally storage-neutral. It does not
    require a particular Knowledge Library implementation and does
    not mutate the Code Library directly.
    """

    def integrate(
        self,
        learning,
    ) -> KnowledgeIntegrationResult:
        if learning is None:
            raise TypeError(
                "learning must not be None"
            )

        if not hasattr(learning, "signals"):
            raise TypeError(
                "learning must expose signals"
            )

        records = []
        record_number = 0

        for signal in learning.signals:
            record_number += 1

            lessons = signal.lessons
            lesson = (
                lessons[0]
                if lessons
                else signal.outcome
            )

            records.append(
                KnowledgeRecord(
                    record_id=(
                        f"outcome-{record_number}-"
                        f"{signal.asset_id}"
                    ),
                    asset_id=signal.asset_id,
                    lesson=lesson,
                    outcome=signal.outcome,
                    score=signal.score,
                    reusable=signal.success,
                    metadata={
                        "step_id": signal.step_id,
                        "lesson_count": len(lessons),
                    },
                )
            )

        records = tuple(records)

        reusable = tuple(
            dict.fromkeys(
                record.asset_id
                for record in records
                if record.reusable
            )
        )

        failed = tuple(
            dict.fromkeys(
                record.asset_id
                for record in records
                if not record.reusable
            )
        )

        lessons = tuple(
            dict.fromkeys(
                record.lesson
                for record in records
            )
        )

        score = (
            learning.score
            if records
            else 0.0
        )

        return KnowledgeIntegrationResult(
            records=records,
            integrated=bool(records),
            reusable_assets=reusable,
            failed_assets=failed,
            lessons=lessons,
            score=score,
            reasons=(
                "outcome_learning_received",
                "knowledge_records_generated",
            )
            if records
            else (
                "no_outcome_signals",
                "knowledge_integration_empty",
            ),
            metadata={
                "record_count": len(records),
                "reusable_count": len(reusable),
                "failed_count": len(failed),
            },
        )

    def build_records(
        self,
        learning,
    ) -> KnowledgeIntegrationResult:
        return self.integrate(learning)

    def integrate_outcomes(
        self,
        learning,
    ) -> KnowledgeIntegrationResult:
        return self.integrate(learning)

    
# Backward-compatible package API aliases.
CodeLibraryKnowledgeRecord = KnowledgeRecord
CodeLibraryKnowledgeIntegrationResult = KnowledgeIntegrationResult
CodeLibraryKnowledgeIntegrator = CodeLibraryKnowledgeIntegrator



__all__ = [
    "KnowledgeRecord",
    "CodeLibraryKnowledgeRecord",
    "KnowledgeIntegrationResult",
    "CodeLibraryKnowledgeIntegrationResult",
    "CodeLibraryKnowledgeIntegrator",
]
