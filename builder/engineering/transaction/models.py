from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class TransactionEvent:
    timestamp: str = field(default_factory=utc_now)
    level: str = "INFO"
    source: str = ""
    message: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class TransactionStage:
    name: str
    status: str = "pending"
    started_at: str = ""
    completed_at: str = ""
    duration: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class EngineeringTransaction:

    id: str = field(default_factory=lambda: uuid4().hex)

    objective: str = ""

    workspace: str = ""

    status: str = "created"

    started_at: str = field(default_factory=utc_now)

    completed_at: str = ""

    changeset_id: str = ""

    execution_result: object | None = None

    runtime_result: object | None = None

    validation: dict = field(default_factory=dict)

    testing: dict = field(default_factory=dict)

    artifacts: list[str] = field(default_factory=list)

    stages: list[TransactionStage] = field(default_factory=list)

    events: list[TransactionEvent] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    rollback_required: bool = False

    def add_stage(self, name: str) -> TransactionStage:
        stage = TransactionStage(name=name)
        self.stages.append(stage)
        return stage

    def stage(self, name: str) -> TransactionStage | None:
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    def add_event(
        self,
        level: str,
        source: str,
        message: str,
        metadata: dict | None = None,
    ):
        self.events.append(
            TransactionEvent(
                level=level,
                source=source,
                message=message,
                metadata=metadata or {},
            )
        )
