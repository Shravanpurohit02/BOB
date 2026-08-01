from builder.execution.scheduler import scheduler

NAME = "Parallel Scheduler"
CATEGORY = "Execution"
DESCRIPTION = "Validates parallel scheduling."


def run() -> bool:

    try:
        Job = type("Job", (), {})

        jobs = []

        for i in range(10):
            job = Job()

            job.id = str(i)
            job.status = "pending"
            job.priority = i
            job.dependencies = []

            jobs.append(job)

        batches = scheduler.schedule_parallel(
            jobs,
            workers=3,
        )

        flattened = [j.id for batch in batches for j in batch]

        return (
            len(batches) == 4
            and len(flattened) == 10
            and flattened == sorted(flattened)
        )

    except Exception:
        return False
