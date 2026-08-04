from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class TransformationRequest:
    id: str = field(default_factory=lambda: uuid4().hex)
    operation: str = ""
    workspace: str = "."
    files: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    transaction: Any | None = None
    preview: bool = False
    validate: bool = True
    write: bool = False


@dataclass(slots=True)
class TransformationDiagnostic:
    severity: str
    message: str
    file: str = ""
    line: int = 0
    column: int = 0
    code: str = ""


@dataclass(slots=True)
class TransformationPreview:
    files: list[str] = field(default_factory=list)
    diff: str = ""
    patches: list[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0


@dataclass(slots=True)
class TransformationMetrics:
    started: float = field(default_factory=perf_counter)
    finished: float = 0.0
    elapsed: float = 0.0
    files_changed: int = 0
    symbols_changed: int = 0

    def stop(self) -> None:
        self.finished = perf_counter()
        self.elapsed = round(self.finished - self.started, 6)


@dataclass(slots=True)
class TransformationResult:
    success: bool = False
    operation: str = ""
    preview: TransformationPreview | None = None
    diagnostics: list[TransformationDiagnostic] = field(default_factory=list)
    metrics: TransformationMetrics = field(default_factory=TransformationMetrics)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_diagnostic(self, severity: str, message: str, *, file: str = "", line: int = 0, column: int = 0, code: str = "") -> None:
        self.diagnostics.append(
            TransformationDiagnostic(
                severity=severity,
                message=message,
                file=file,
                line=line,
                column=column,
                code=code,
            )
        )

    @property
    def has_errors(self) -> bool:
        return any(d.severity.lower() == "error" for d in self.diagnostics)


__all__ = [
    "TransformationRequest",
    "TransformationDiagnostic",
    "TransformationPreview",
    "TransformationMetrics",
    "TransformationResult",
]
