from builder.execution.snapshot.models import (
    ExecutionCheckpoint,
    ExecutionSnapshot,
)
from builder.execution.snapshot.recovery import recovery

NAME = "Execution Resume"
CATEGORY = "Execution"
DESCRIPTION = "Validates execution resume stage detection."


def run() -> bool:

    try:
        snapshot = ExecutionSnapshot()

        snapshot.checkpoints = [
            ExecutionCheckpoint(
                stage="changeset",
                status="completed",
            ),
            ExecutionCheckpoint(
                stage="output",
                status="completed",
            ),
        ]

        stage = recovery.next_stage(
            snapshot,
            [
                "changeset",
                "output",
                "planning",
                "validation",
                "testing",
            ],
        )

        return stage == "planning"

    except Exception:
        return False
