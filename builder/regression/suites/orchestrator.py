from builder.execution.scheduler import scheduler

NAME = "Orchestrator"
CATEGORY = "Execution"
DESCRIPTION = "Validates scheduler orchestration."


def run() -> bool:

    try:
        Job = type(
            "Job",
            (),
            {},
        )

        jobs = []

        for priority in (3, 1, 2):
            job = Job()

            job.id = str(priority)
            job.status = "pending"
            job.priority = priority
            job.dependencies = []

            jobs.append(job)

        ordered = scheduler.schedule(
            jobs,
        )

        return [j.priority for j in ordered] == [1, 2, 3]

    except Exception:
        return False
