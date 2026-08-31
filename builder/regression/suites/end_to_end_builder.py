from builder.planning.executor import executor
from builder.planning.models import (
    EngineeringPlan,
    Job,
    Milestone,
    Task,
)

NAME = "End-to-End Builder"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates complete Builder planning workflow."


def run() -> bool:

    try:
        plan = EngineeringPlan()

        milestone = Milestone(
            title="End-to-End",
        )

        job = Job(
            title="Builder",
        )

        job.tasks.extend(
            [
                Task(
                    title="planner.py",
                    priority=1,
                ),
                Task(
                    title="executor.py",
                    priority=2,
                ),
                Task(
                    title="validator.py",
                    priority=3,
                ),
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

        return (
            execution.completed == 3
            and execution.failed == 0
            and execution.total == 3
            and len(execution.executed) == 3
            and execution.analytics.tasks == 3
            and execution.analytics.completed == 3
            and len(execution.analytics.repository.files) == 3
        )

    except Exception:
        return False
