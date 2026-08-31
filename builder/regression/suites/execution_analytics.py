from builder.planning.executor import executor
from builder.planning.models import (
    EngineeringPlan,
    Job,
    Milestone,
    Task,
)

NAME = "Execution Analytics"
CATEGORY = "Planning"
DESCRIPTION = "Validates execution analytics collection."


def run() -> bool:

    try:
        plan = EngineeringPlan()

        milestone = Milestone()

        job = Job()

        job.tasks.append(
            Task(
                title="analytics",
            )
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

        return (
            execution.analytics.tasks == 1
            and execution.analytics.completed == 1
            and len(execution.analytics.decisions) == 1
        )

    except Exception:
        return False
