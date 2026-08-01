from builder.planning.executor import executor
from builder.planning.models import Task

NAME = "Multi-Agent Coordination"
CATEGORY = "Planning"
DESCRIPTION = "Validates autonomous agent coordination."


def run() -> bool:

    try:
        tasks = [
            Task(title="planner"),
            Task(title="engineer"),
            Task(title="reviewer"),
            Task(title="validator"),
        ]

        assignments = executor._coordinate_agents(
            tasks,
        )

        expected = [
            "planner",
            "engineer",
            "reviewer",
            "validator",
        ]

        return (
            len(assignments) == 4
            and [task.metadata.get("agent") for task in tasks] == expected
        )

    except Exception:
        return False
