from builder.planning.executor import executor
from builder.planning.models import Task

NAME = "Autonomous Code Evolution"
CATEGORY = "Planning"
DESCRIPTION = "Validates autonomous task evolution."


def run() -> bool:

    try:
        task = Task(
            title="evolve",
        )

        task.status = "completed"

        executor._evolve_task(
            task,
        )

        evolution = task.metadata.get(
            "evolution",
            [],
        )

        return (
            len(evolution) == 1
            and evolution[0]["status"] == "completed"
            and evolution[0]["retries"] == 0
        )

    except Exception:
        return False
