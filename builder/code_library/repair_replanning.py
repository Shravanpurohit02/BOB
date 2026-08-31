from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .execution_result_verification import (
    ExecutionVerificationResult,
    VerificationResult,
)


@dataclass(frozen=True)
class RepairAction:
    step_id: str
    asset_id: str
    action: str
    reason: str
    priority: int = 1
    retryable: bool = True
    metadata: dict = None

    def __post_init__(self):
        if not self.step_id:
            raise ValueError("step_id must not be empty")
        if not self.asset_id:
            raise ValueError("asset_id must not be empty")
        if not self.action:
            raise ValueError("action must not be empty")
        if not self.reason:
            raise ValueError("reason must not be empty")
        if self.priority < 1:
            raise ValueError("priority must be >= 1")

        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "asset_id": self.asset_id,
            "action": self.action,
            "reason": self.reason,
            "priority": self.priority,
            "retryable": self.retryable,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class RepairPlan:
    actions: tuple[RepairAction, ...]
    blocked: bool
    replanning_required: bool
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "actions": [
                action.to_dict()
                for action in self.actions
            ],
            "blocked": self.blocked,
            "replanning_required": (
                self.replanning_required
            ),
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryRepairReplanner:
    """
    Converts failed execution verification into deterministic repair
    actions and a bounded replanning decision.

    The component does not execute repairs. It produces the next
    construction actions for the execution layer.
    """

    _RETRYABLE_REASONS = frozenset(
        {
            "execution_output_invalid",
            "repository_state_invalid",
            "execution_result_not_verified",
        }
    )

    _BLOCKING_REASONS = frozenset(
        {
            "execution_not_performed",
        }
    )

    def _repair_for_result(
        self,
        result: VerificationResult,
    ) -> RepairAction | None:
        if result.verified:
            return None

        if (
            "execution_not_performed"
            in result.reasons
        ):
            return RepairAction(
                step_id=result.step_id,
                asset_id=result.asset_id,
                action="replan_execution",
                reason="execution_not_performed",
                priority=1,
                retryable=False,
                metadata={
                    "verification_reasons": list(
                        result.reasons
                    ),
                },
            )

        if (
            "repository_state_invalid"
            in result.reasons
        ):
            return RepairAction(
                step_id=result.step_id,
                asset_id=result.asset_id,
                action="repair_repository_state",
                reason="repository_state_invalid",
                priority=1,
                retryable=True,
                metadata={
                    "verification_reasons": list(
                        result.reasons
                    ),
                },
            )

        if (
            "execution_output_invalid"
            in result.reasons
        ):
            return RepairAction(
                step_id=result.step_id,
                asset_id=result.asset_id,
                action="retry_execution",
                reason="execution_output_invalid",
                priority=2,
                retryable=True,
                metadata={
                    "verification_reasons": list(
                        result.reasons
                    ),
                },
            )

        if (
            "execution_result_not_verified"
            in result.reasons
        ):
            return RepairAction(
                step_id=result.step_id,
                asset_id=result.asset_id,
                action="reverify_execution",
                reason="execution_result_not_verified",
                priority=3,
                retryable=True,
                metadata={
                    "verification_reasons": list(
                        result.reasons
                    ),
                },
            )

        return RepairAction(
            step_id=result.step_id,
            asset_id=result.asset_id,
            action="replan_construction",
            reason="unclassified_verification_failure",
            priority=1,
            retryable=False,
            metadata={
                "verification_reasons": list(
                    result.reasons
                ),
            },
        )

    def build_plan(
        self,
        verification: ExecutionVerificationResult,
    ) -> RepairPlan:
        if not isinstance(
            verification,
            ExecutionVerificationResult,
        ):
            raise TypeError(
                "verification must be "
                "ExecutionVerificationResult"
            )

        if verification.verified:
            return RepairPlan(
                actions=(),
                blocked=False,
                replanning_required=False,
                score=10.0,
                reasons=(
                    "execution_verified",
                    "repair_not_required",
                ),
                metadata={
                    "verification_count": len(
                        verification.results
                    ),
                    "repair_count": 0,
                },
            )

        if not verification.results:
            return RepairPlan(
                actions=(),
                blocked=True,
                replanning_required=True,
                score=0.0,
                reasons=(
                    "no_verification_results",
                    "repair_blocked",
                    "replanning_required",
                ),
                metadata={
                    "verification_count": 0,
                    "repair_count": 0,
                },
            )

        actions = []

        for result in verification.results:
            action = self._repair_for_result(
                result
            )

            if action is not None:
                actions.append(action)

        actions.sort(
            key=lambda item: (
                item.priority,
                item.step_id,
                item.asset_id,
            )
        )

        blocked = any(
            not action.retryable
            for action in actions
        )

        score = (
            10.0
            if not actions
            else max(
                0.0,
                10.0
                - (
                    min(
                        10.0,
                        len(actions)
                        * 2.0,
                    )
                ),
            )
        )

        reasons = [
            "verification_failure_received",
            "repair_actions_generated",
        ]

        if blocked:
            reasons.append(
                "repair_contains_blocking_action"
            )

        reasons.append(
            "replanning_required"
        )

        return RepairPlan(
            actions=tuple(actions),
            blocked=blocked,
            replanning_required=True,
            score=score,
            reasons=tuple(reasons),
            metadata={
                "verification_count": len(
                    verification.results
                ),
                "repair_count": len(actions),
                "retryable_count": sum(
                    1
                    for action in actions
                    if action.retryable
                ),
                "blocking_count": sum(
                    1
                    for action in actions
                    if not action.retryable
                ),
            },
        )

    def replan(
        self,
        verification: ExecutionVerificationResult,
    ) -> RepairPlan:
        return self.build_plan(
            verification
        )

    def repair(
        self,
        verification: ExecutionVerificationResult,
    ) -> RepairPlan:
        return self.build_plan(
            verification
        )


__all__ = [
    "RepairAction",
    "RepairPlan",
    "CodeLibraryRepairReplanner",
]
