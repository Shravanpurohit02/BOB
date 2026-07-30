from builder.execution.context import ExecutionContext
from builder.execution.executor import executor
from builder.execution.scheduler import scheduler

class Pipeline:

    def run(self):
        job = scheduler.next_job()

        if job is None:
            return None

        jobs = __import__("builder.core.jobs", fromlist=["jobs"]).jobs

        jobs.start(job.id)

        context = ExecutionContext(
            job_id=job.id,
            worker_id=job.worker,
        )

        result = executor.execute(context)

        jobs.complete(job.id)

        return result

pipeline = Pipeline()
