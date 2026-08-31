from builder.planning.executor import executor
from builder.planning.models import (
    EngineeringPlan,
    Job,
    Milestone,
    Task,
)

NAME = "Repository Engineering"
CATEGORY = "Planning"
DESCRIPTION = "Validates repository engineering analytics."


def run() -> bool:

    try:
        plan = EngineeringPlan()

        milestone = Milestone()

        job = Job()

        job.tasks.append(
            Task(
                title="builder/core/jobs.py",
            )
        )

        job.tasks.append(
            Task(
                title="builder/planning/executor.py",
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

        repository = execution.analytics.repository

        return len(repository.files) == 2 and "builder" in repository.modules

    except Exception:
        return False
