from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass(slots=True, frozen=True)
class ValidationIssue:
    validator: str
    severity: Severity
    message: str
    file: str = ""
    line: int = 0
    column: int = 0
    code: str = ""
    suggestion: str = ""


@dataclass(slots=True)
class ValidationResult:
    validator: str
    status: ValidationStatus
    issues: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is ValidationStatus.PASS

    @property
    def failed(self) -> bool:
        return self.status is ValidationStatus.FAIL

    @classmethod
    def success(
        cls,
        validator: str,
        metadata: dict[str, Any] | None = None,
    ) -> "ValidationResult":
        return cls(
            validator=validator,
            status=ValidationStatus.PASS,
            metadata=metadata or {},
        )

    @classmethod
    def failure(
        cls,
        validator: str,
        issues: list[ValidationIssue],
        metadata: dict[str, Any] | None = None,
    ) -> "ValidationResult":
        return cls(
            validator=validator,
            status=ValidationStatus.FAIL,
            issues=issues,
            metadata=metadata or {},
        )


@dataclass(slots=True)
class ValidationRequest:
    workspace: Path
    patch: dict[str, Any]
    repository: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationContext:
    config: Any | None = None
    state: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GuardrailReport:
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(result.failed for result in self.results)

    @property
    def failed(self) -> bool:
        return not self.passed

    @property
    def errors(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for result in self.results:
            issues.extend(
                issue
                for issue in result.issues
                if issue.severity in (
                    Severity.ERROR,
                    Severity.CRITICAL,
                )
            )
        return issues

    @property
    def warnings(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for result in self.results:
            issues.extend(
                issue
                for issue in result.issues
                if issue.severity is Severity.WARNING
            )
        return issues

    def add(self, result: ValidationResult) -> None:
        self.results.append(result)
