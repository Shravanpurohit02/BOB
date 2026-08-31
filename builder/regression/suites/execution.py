from builder.execution.context import ExecutionContext
from builder.execution.executor import executor

NAME = "Execution"
CATEGORY = "Foundation"
DESCRIPTION = "Validates execution engine."


def run() -> bool:

    try:
        ctx = ExecutionContext(
            plan_id="regression-plan",
            worker_id="regression-worker",
            job_id="regression-job",
        )

        execution = executor.execute(ctx)

        return (
            execution.success is True
            and execution.message == "completed"
            and len(execution.failed_stages) == 0
            and execution.validation.get("failed", 0) == 0
            and execution.testing.get("failed", 0) == 0
            and len(execution.artifacts) > 0
            and bool(execution.changeset)
            and ctx.plan_id == "regression-plan"
            and ctx.worker_id == "regression-worker"
            and ctx.job_id == "regression-job"
        )

    except Exception:
        return False
