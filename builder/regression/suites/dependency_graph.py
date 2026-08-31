from builder.planning.executor import executor
from builder.planning.models import (
    EngineeringPlan,
    Job,
    Milestone,
    Task,
)

NAME = "Dependency Graph"
CATEGORY = "Planning"
DESCRIPTION = "Validates dependency-aware execution ordering."


def run() -> bool:

    try:
        plan = EngineeringPlan()

        milestone = Milestone()

        job = Job()

        first = Task(
            title="first",
            priority=1,
        )

        second = Task(
            title="second",
            priority=2,
            dependencies=[first.id],
        )

        third = Task(
            title="third",
            priority=3,
            dependencies=[second.id],
        )

        job.tasks.extend(
            [
                third,
                second,
                first,
            ]
        )

        milestone.jobs.append(
            job,
        )

        plan.milestones.append(
            milestone,
        )

        execution = executor.execute(
            plan,
        )

        return execution.executed == [
            "first",
            "second",
            "third",
        ]

    except Exception:
        return False
