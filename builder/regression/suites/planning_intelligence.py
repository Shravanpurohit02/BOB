from builder.planning.executor import executor
from builder.planning.models import (
    EngineeringPlan,
    Job,
    Milestone,
    Task,
)

NAME = "Planning Intelligence"
CATEGORY = "Planning"
DESCRIPTION = "Validates task prioritization within engineering plans."


def run() -> bool:

    try:
        plan = EngineeringPlan()

        milestone = Milestone()

        job = Job()

        low = Task(
            title="low",
            priority=50,
        )

        high = Task(
            title="high",
            priority=1,
        )

        job.tasks.extend(
            [
                low,
                high,
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
            "high",
            "low",
        ]

    except Exception:
        return False
