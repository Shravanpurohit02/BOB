from __future__ import annotations

from dataclasses import dataclass, field

from builder.intelligence.refactoring_planner import (
    RefactoringPlan,
)


@dataclass(slots=True)
class EngineeringOperation:
    """
    Operation consumable by ChangeExecutor.
    """

    operation: str

    file: str

    metadata: dict = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class EngineeringPlan:
    """
    ChangeExecutor-compatible engineering plan.
    """

    operations: list[EngineeringOperation] = field(
        default_factory=list,
    )

    @property
    def total(self) -> int:
        return len(self.operations)


class RefactoringBridge:
    """
    Converts RefactoringPlan into a ChangeExecutor-compatible plan.
    """

    def build(
        self,
        plan: RefactoringPlan,
    ) -> EngineeringPlan:

        engineering = EngineeringPlan()

        for operation in plan.operations:

            engineering.operations.append(
                EngineeringOperation(
                    operation=operation.operation,
                    file=operation.file,
                    metadata={
                        "rule": operation.rule,
                        "line": operation.line,
                        "column": operation.column,
                        "message": operation.message,
                    },
                )
            )

        return engineering


refactoring_bridge = RefactoringBridge()

__all__ = (
    "EngineeringOperation",
    "EngineeringPlan",
    "RefactoringBridge",
    "refactoring_bridge",
)
