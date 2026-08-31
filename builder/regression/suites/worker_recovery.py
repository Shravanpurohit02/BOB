from builder.execution.scheduler import worker_pool

NAME = "Worker Recovery"
CATEGORY = "Execution"
DESCRIPTION = "Validates automatic worker recovery."


def run() -> bool:

    try:
        worker_pool.scale(4)

        worker = worker_pool.workers[0]

        worker["status"] = "failed"

        recovered = worker_pool.recover_workers()

        metrics = worker_pool.metrics()

        return (
            recovered == 1
            and worker["status"] == "idle"
            and metrics["healthy"] == 4
            and metrics["workers"] == 4
        )

    except Exception:
        return False
