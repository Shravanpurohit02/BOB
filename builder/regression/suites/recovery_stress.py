from builder.execution.snapshot.models import ExecutionSnapshot
from builder.execution.snapshot.recovery import recovery

NAME = "Recovery Stress"
CATEGORY = "Execution"
DESCRIPTION = "Validates recovery engine under stress."


def run() -> bool:

    try:
        snapshots = []

        for i in range(100):
            s = ExecutionSnapshot()

            s.status = "completed" if i % 2 else "running"

            snapshots.append(s)

        active = [s for s in snapshots if s.status in recovery.ACTIVE]

        return len(active) == 50

    except Exception:
        return False
