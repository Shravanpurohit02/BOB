from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .execution_integration import (
    ExecutionIntegrationResult,
)
from .execution_result_verification import (
    ExecutionVerificationResult,
)
from .repair_replanning import RepairPlan


@dataclass(frozen=True)
class OutcomeSignal:
    step_id: str
    asset_id: str
    outcome: str
    success: bool
    score: float
    lessons: tuple[str, ...]
    metadata: dict

    def __post_init__(self):
        if not self.step_id:
            raise ValueError("step_id must not be empty")
        if not self.asset_id:
            raise ValueError("asset_id must not be empty")
        if not self.outcome:
            raise ValueError("outcome must not be empty")

        if not 0.0 <= self.score <= 10.0:
            raise ValueError(
                "score must be between 0.0 and 10.0"
            )

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "asset_id": self.asset_id,
            "outcome": self.outcome,
            "success": self.success,
            "score": self.score,
            "lessons": list(self.lessons),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class OutcomeLearningResult:
    requirement_name: str
    signals: tuple[OutcomeSignal, ...]
    learned: bool
    successful: bool
    score: float
    lessons: tuple[str, ...]
    reusable_assets: tuple[str, ...]
    retryable_assets: tuple[str, ...]
    blocked_assets: tuple[str, ...]
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "requirement_name": self.requirement_name,
            "signals": [
                signal.to_dict()
                for signal in self.signals
            ],
            "learned": self.learned,
            "successful": self.successful,
            "score": self.score,
            "lessons": list(self.lessons),
            "reusable_assets": list(
                self.reusable_assets
            ),
            "retryable_assets": list(
                self.retryable_assets
            ),
            "blocked_assets": list(
                self.blocked_assets
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryOutcomeLearner:
    """
    Converts execution, verification, and repair outcomes into
    deterministic reusable learning signals.

    This component does not mutate the Code Library. It produces
    structured learning information that a future knowledge/index
    layer can persist and reuse.
    """

    def _execution_signal(
        self,
        result,
    ) -> OutcomeSignal:
        if result.success:
            outcome = "execution_success"
            lessons = (
                "asset_execution_successful",
                "asset_candidate_reusable",
            )
        else:
            outcome = "execution_failure"
            lessons = (
                "asset_execution_failed",
                "asset_requires_repair",
            )

        return OutcomeSignal(
            step_id=result.step_id,
            asset_id=result.asset_id,
            outcome=outcome,
            success=result.success,
            score=(
                10.0
                if result.success
                else 0.0
            ),
            lessons=lessons,
            metadata={
                "exit_code": result.exit_code,
                "output_length": len(
                    result.output
                ),
                "error_length": len(
                    result.error
                ),
            },
        )

    def learn_from_execution(
        self,
        execution: ExecutionIntegrationResult,
    ) -> OutcomeLearningResult:
        if not isinstance(
            execution,
            ExecutionIntegrationResult,
        ):
            raise TypeError(
                "execution must be "
                "ExecutionIntegrationResult"
            )

        if not execution.results:
            return OutcomeLearningResult(
                requirement_name=(
                    execution.requirement_name
                ),
                signals=(),
                learned=False,
                successful=False,
                score=0.0,
                lessons=(),
                reusable_assets=(),
                retryable_assets=(),
                blocked_assets=(),
                reasons=(
                    "no_execution_results",
                    "learning_not_available",
                ),
                metadata={
                    "signal_count": 0,
                },
            )

        signals = tuple(
            self._execution_signal(result)
            for result in execution.results
        )

        reusable = tuple(
            signal.asset_id
            for signal in signals
            if signal.success
        )

        retryable = tuple(
            signal.asset_id
            for signal in signals
            if not signal.success
        )

        lessons = tuple(
            dict.fromkeys(
                lesson
                for signal in signals
                for lesson in signal.lessons
            )
        )

        successful = (
            execution.successful
            and all(
                signal.success
                for signal in signals
            )
        )

        score = (
            10.0
            if successful
            else (
                10.0
                * (
                    len(reusable)
                    / len(signals)
                )
            )
        )

        return OutcomeLearningResult(
            requirement_name=(
                execution.requirement_name
            ),
            signals=signals,
            learned=True,
            successful=successful,
            score=score,
            lessons=lessons,
            reusable_assets=reusable,
            retryable_assets=retryable,
            blocked_assets=(),
            reasons=(
                "execution_outcomes_received",
                "outcome_signals_generated",
                "lessons_extracted",
            ),
            metadata={
                "signal_count": len(signals),
                "successful_count": len(reusable),
                "failed_count": len(retryable),
            },
        )

    def learn_from_verification(
        self,
        verification: ExecutionVerificationResult,
    ) -> OutcomeLearningResult:
        if not isinstance(
            verification,
            ExecutionVerificationResult,
        ):
            raise TypeError(
                "verification must be "
                "ExecutionVerificationResult"
            )

        if not verification.results:
            return OutcomeLearningResult(
                requirement_name=(
                    verification.requirement_name
                ),
                signals=(),
                learned=False,
                successful=False,
                score=0.0,
                lessons=(),
                reusable_assets=(),
                retryable_assets=(),
                blocked_assets=(),
                reasons=(
                    "no_verification_results",
                    "learning_not_available",
                ),
                metadata={
                    "signal_count": 0,
                },
            )

        signals = []

        for result in verification.results:
            if result.verified:
                outcome = "verification_success"
                lessons = (
                    "asset_verified",
                    "asset_reusable",
                )
                score = 10.0
            else:
                outcome = "verification_failure"
                lessons = (
                    "asset_verification_failed",
                    "asset_requires_replanning",
                )
                score = 0.0

            signals.append(
                OutcomeSignal(
                    step_id=result.step_id,
                    asset_id=result.asset_id,
                    outcome=outcome,
                    success=result.verified,
                    score=score,
                    lessons=lessons,
                    metadata={
                        "output_valid": (
                            result.output_valid
                        ),
                        "repository_valid": (
                            result.repository_valid
                        ),
                    },
                )
            )

        signals = tuple(signals)

        reusable = tuple(
            signal.asset_id
            for signal in signals
            if signal.success
        )

        retryable = tuple(
            signal.asset_id
            for signal in signals
            if not signal.success
        )

        lessons = tuple(
            dict.fromkeys(
                lesson
                for signal in signals
                for lesson in signal.lessons
            )
        )

        successful = (
            verification.verified
            and all(
                signal.success
                for signal in signals
            )
        )

        score = (
            10.0
            if successful
            else (
                10.0
                * (
                    len(reusable)
                    / len(signals)
                )
            )
        )

        return OutcomeLearningResult(
            requirement_name=(
                verification.requirement_name
            ),
            signals=signals,
            learned=True,
            successful=successful,
            score=score,
            lessons=lessons,
            reusable_assets=reusable,
            retryable_assets=retryable,
            blocked_assets=(),
            reasons=(
                "verification_outcomes_received",
                "verification_signals_generated",
                "lessons_extracted",
            ),
            metadata={
                "signal_count": len(signals),
                "verified_count": len(reusable),
                "failed_count": len(retryable),
            },
        )

    def learn_from_repair(
        self,
        repair: RepairPlan,
    ) -> OutcomeLearningResult:
        if not isinstance(
            repair,
            RepairPlan,
        ):
            raise TypeError(
                "repair must be RepairPlan"
            )

        if not repair.actions:
            return OutcomeLearningResult(
                requirement_name="",
                signals=(),
                learned=True,
                successful=not repair.replanning_required,
                score=(
                    10.0
                    if not repair.replanning_required
                    else repair.score
                ),
                lessons=(
                    "repair_not_required",
                ),
                reusable_assets=(),
                retryable_assets=(),
                blocked_assets=(),
                reasons=(
                    "no_repair_actions",
                    "repair_outcome_learned",
                ),
                metadata={
                    "signal_count": 0,
                },
            )

        signals = []

        for action in repair.actions:
            if action.retryable:
                outcome = "repair_retryable"
                lessons = (
                    "asset_retryable",
                    "repair_action_available",
                )
            else:
                outcome = "repair_blocked"
                lessons = (
                    "asset_repair_blocked",
                    "construction_requires_replanning",
                )

            signals.append(
                OutcomeSignal(
                    step_id=action.step_id,
                    asset_id=action.asset_id,
                    outcome=outcome,
                    success=False,
                    score=0.0,
                    lessons=lessons,
                    metadata={
                        "action": action.action,
                        "priority": action.priority,
                        "retryable": action.retryable,
                    },
                )
            )

        signals = tuple(signals)

        retryable = tuple(
            signal.asset_id
            for signal in signals
            if signal.metadata.get(
                "retryable",
                False,
            )
        )

        blocked = tuple(
            signal.asset_id
            for signal in signals
            if not signal.metadata.get(
                "retryable",
                False,
            )
        )

        lessons = tuple(
            dict.fromkeys(
                lesson
                for signal in signals
                for lesson in signal.lessons
            )
        )

        return OutcomeLearningResult(
            requirement_name="",
            signals=signals,
            learned=True,
            successful=False,
            score=repair.score,
            lessons=lessons,
            reusable_assets=(),
            retryable_assets=retryable,
            blocked_assets=blocked,
            reasons=(
                "repair_outcomes_received",
                "repair_signals_generated",
                "repair_lessons_extracted",
            ),
            metadata={
                "signal_count": len(signals),
                "retryable_count": len(retryable),
                "blocked_count": len(blocked),
            },
        )


__all__ = [
    "OutcomeSignal",
    "OutcomeLearningResult",
    "CodeLibraryOutcomeLearner",
]
