from .planner import planner

class PlanningEngine:

    def create(
        self,
        objective: str,
        workspace: str = ".",
        metadata: dict | None = None,
    ):
        plan = planner.create(objective)
        plan.workspace = workspace
        plan.metadata = metadata or {}
        return plan

    def add_milestone(self, plan, title):
        from .models import Milestone
        milestone = Milestone(title=title)
        plan.milestones.append(milestone)
        return milestone

    def add_job(self, milestone, title):
        from .models import Job
        job = Job(title=title)
        milestone.jobs.append(job)
        return job

    def add_task(self, job, title, objective=""):
        from .models import Task
        task = Task(
            title=title,
            objective=objective or title,
        )
        job.tasks.append(task)
        return task

    def tasks(self, plan):
        result = []
        for milestone in plan.milestones:
            for job in milestone.jobs:
                result.extend(job.tasks)
        return result

engine = PlanningEngine()
