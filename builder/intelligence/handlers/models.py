from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class HandlerStatus(str, Enum):
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


@dataclass(slots=True)
class HandlerArtifact:
    """
    Artifact produced by a handler.
    """

    path: str
    kind: str = "file"
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class HandlerMetrics:
    """
    Execution metrics for a handler.
    """

    started_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    finished_at: str = ""

    duration: float = 0.0

    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class HandlerResult:
    """
    Canonical execution result returned by every handler.
    """

    success: bool

    status: HandlerStatus

    operation: str

    file: str

    message: str = ""

    patch_id: str = ""

    backup: str = ""

    diff: str = ""

    error: str = ""

    artifacts: list[HandlerArtifact] = field(default_factory=list)

    metrics: HandlerMetrics = field(default_factory=HandlerMetrics)

    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class HandlerContext:
    """
    Shared execution context supplied to handlers.
    """

    workspace: str

    transaction: object | None = None

    metadata: dict = field(default_factory=dict)
