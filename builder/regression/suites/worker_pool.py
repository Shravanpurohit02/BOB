from builder.execution.scheduler import worker_pool

NAME = "Worker Pool"
CATEGORY = "Execution"
DESCRIPTION = "Validates worker acquisition and release."


def run() -> bool:

    try:
        worker = worker_pool.acquire()

        ok = worker is not None and worker["status"] == "busy"

        if worker is not None:
            worker_pool.release(
                worker["id"],
            )

            ok = ok and worker["status"] == "idle"

        return ok

    except Exception:
        return False
