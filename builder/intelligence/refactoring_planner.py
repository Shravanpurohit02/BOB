from __future__ import annotations

from dataclasses import dataclass, field

from builder.intelligence.lint_diagnostics import (
    LintReport,
)
from builder.intelligence.lint_rules import (
    lint_rule_registry,
)


@dataclass(slots=True)
class RefactoringOperation:
    """
    Planned engineering operation produced from a lint diagnostic.
    """

    operation: str
    rule: str
    file: str
    line: int
    column: int
    message: str


@dataclass(slots=True)
class RefactoringPlan:
    """
    Collection of planned engineering operations.
    """

    operations: list[RefactoringOperation] = field(
        default_factory=list,
    )

    @property
    def total(self) -> int:
        return len(self.operations)


class RefactoringPlanner:
    """
    Converts lint diagnostics into engineering operations.
    """

    def create_plan(
        self,
        report: LintReport,
    ) -> RefactoringPlan:

        plan = RefactoringPlan()

        for diagnostic in report.diagnostics:

            rule = lint_rule_registry.get(
                diagnostic.rule,
            )

            if rule is None:
                continue

            plan.operations.append(
                RefactoringOperation(
                    operation=rule.operation,
                    rule=diagnostic.rule,
                    file=diagnostic.file,
                    line=diagnostic.line,
                    column=diagnostic.column,
                    message=diagnostic.message,
                )
            )

        return plan


refactoring_planner = RefactoringPlanner()

__all__ = (
    "RefactoringOperation",
    "RefactoringPlan",
    "RefactoringPlanner",
    "refactoring_planner",
)
