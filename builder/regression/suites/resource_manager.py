from builder.execution.scheduler import worker_pool

NAME = "Resource Manager"
CATEGORY = "Execution"
DESCRIPTION = "Validates worker pool scaling and health metrics."


def run() -> bool:

    try:
        worker_pool.scale(6)

        metrics = worker_pool.health()

        ok = (
            metrics["workers"] == 6
            and metrics["healthy"] == 6
            and metrics["busy"] == 0
            and metrics["idle"] == 6
        )

        worker_pool.scale(4)

        return ok

    except Exception:
        return False
