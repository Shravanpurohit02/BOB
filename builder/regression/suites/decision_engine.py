from builder.planning.executor import executor
from builder.planning.models import Task

NAME = "Decision Engine"
CATEGORY = "Planning"
DESCRIPTION = "Validates execution decision routing."


def run() -> bool:

    try:
        standard = Task(
            title="standard",
        )

        priority = Task(
            title="priority",
            priority=1,
        )

        dependency = Task(
            title="dependency",
            dependencies=["abc"],
        )

        return (
            executor._decision(standard) == "standard"
            and executor._decision(priority) == "priority"
            and executor._decision(dependency) == "dependency"
        )

    except Exception:
        return False
