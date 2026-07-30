from .models import (
    EngineeringPlan,
    Milestone,
    Job,
    Task,
)


class Planner:

    def create(
        self,
        objective:str,
    ):

        plan=EngineeringPlan(
            objective=objective,
        )

        milestone=Milestone(
            title="Implementation",
        )

        job=Job(
            title="Engineering",
        )

        job.tasks.append(
            Task(
                title=objective,
                objective=objective,
            )
        )

        milestone.jobs.append(job)

        plan.milestones.append(
            milestone
        )

        return plan


planner=Planner()
