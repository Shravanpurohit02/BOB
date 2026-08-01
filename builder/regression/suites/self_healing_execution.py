from builder.planning.executor import executor
from builder.planning.models import Task

NAME = "Self-Healing Execution"
CATEGORY = "Planning"
DESCRIPTION = "Validates retry, backoff and automatic recovery."


def run() -> bool:

    try:
        task = Task()

        attempts = {"count": 0}

        def action(_):

            attempts["count"] += 1

            if attempts["count"] < 3:
                raise TimeoutError()

        ok = executor._execute_task(
            task,
            action,
        )

        return (
            ok
            and task.status == "completed"
            and task.retries == 2
            and task.metadata.get("failure") == "transient"
            and task.metadata.get("backoff") == 4
        )

    except Exception:
        return False
