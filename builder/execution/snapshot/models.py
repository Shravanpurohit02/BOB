from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class ExecutionCheckpoint:

    stage: str = ""

    status: str = "pending"

    started_at: str = ""

    completed_at: str = ""

    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionSnapshot:

    id: str = field(default_factory=lambda: uuid4().hex)

    transaction_id: str = ""

    execution_id: str = ""

    objective: str = ""

    workspace: str = "."

    status: str = "created"

    current_stage: str = ""

    plan_id: str = ""

    changeset_id: str = ""

    validation: dict = field(default_factory=dict)

    testing: dict = field(default_factory=dict)

    artifacts: list[str] = field(default_factory=list)

    checkpoints: list[ExecutionCheckpoint] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    created_at: str = field(default_factory=utc_now)

    updated_at: str = field(default_factory=utc_now)

    completed_at: str = ""

    def checkpoint(
        self,
        stage: str,
    ) -> ExecutionCheckpoint:

        cp = ExecutionCheckpoint(
            stage=stage,
            status="running",
            started_at=utc_now(),
        )

        self.current_stage = stage

        self.updated_at = utc_now()

        self.checkpoints.append(cp)

        return cp

    def complete_stage(
        self,
        stage: str,
    ):

        for cp in reversed(self.checkpoints):

            if cp.stage == stage:

                cp.status = "completed"

                cp.completed_at = utc_now()

                break

        self.updated_at = utc_now()
