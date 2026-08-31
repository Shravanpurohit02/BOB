from builder.planning.executor import executor
from builder.planning.models import Task

NAME = "Failure Classification"
CATEGORY = "Planning"
DESCRIPTION = "Validates failure classification and retry budget."


def run() -> bool:

    try:
        transient = executor._classify_failure(TimeoutError())

        permanent = executor._classify_failure(ValueError())

        task = Task()

        task.retries = 1

        budget = executor._retry_budget(
            task,
        )

        return transient == "transient" and permanent == "permanent" and budget == 2

    except Exception:
        return False
