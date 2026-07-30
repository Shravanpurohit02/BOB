from builder.core.jobs import jobs

class Scheduler:

    def next_job(self):
        items = jobs.all()
        for job in items:
            if job.status == "pending":
                return job
        return None

    def schedule(
        self,
        jobs,
    ):

        pending = [
            j
            for j in jobs
            if getattr(
                j,
                "status",
                "pending",
            ) == "pending"
        ]

        pending.sort(
            key=lambda j: (
                len(
                    getattr(
                        j,
                        "dependencies",
                        [],
                    )
                ),
                getattr(
                    j,
                    "priority",
                    100,
                ),
                getattr(
                    j,
                    "id",
                    "",
                ),
            )
        )

        return pending


    def schedule_parallel(
        self,
        jobs,
        workers=4,
    ):

        queue = self.schedule(jobs)

        batches = []

        while queue:

            batch = []

            while (
                queue
                and len(batch) < workers
            ):
                batch.append(
                    queue.pop(0)
                )

            batches.append(batch)

        return batches



class WorkerPool:

    def __init__(
        self,
        size=4,
    ):
        self.size = size

        self.workers = [
            {
                "id": f"worker-{i+1}",
                "status": "idle",
                "jobs": 0,
            }
            for i in range(size)
        ]

    def scale(
        self,
        target_size,
    ):

        if target_size < 1:
            target_size = 1

        current = len(self.workers)

        if target_size > current:

            for i in range(current, target_size):

                self.workers.append(
                    {
                        "id": f"worker-{i+1}",
                        "status": "idle",
                        "jobs": 0,
                    }
                )

        elif target_size < current:

            removable = [
                w
                for w in self.workers
                if w["status"] == "idle"
            ]

            while (
                len(self.workers) > target_size
                and removable
            ):
                worker = removable.pop()
                self.workers.remove(worker)

        self.size = len(self.workers)

        return self.size


    def acquire(self):

        for worker in self.workers:

            if worker["status"] == "idle":

                worker["status"] = "busy"

                worker["jobs"] += 1

                return worker

        return None

    def health(
        self,
    ):

        healthy = 0
        busy = 0
        idle = 0

        for worker in self.workers:

            if worker["status"] == "busy":
                busy += 1
            else:
                idle += 1

            healthy += 1

        return {
            "workers": len(self.workers),
            "healthy": healthy,
            "busy": busy,
            "idle": idle,
            "utilization": (
                busy / len(self.workers)
                if self.workers
                else 0.0
            ),
        }


    def release(
        self,
        worker_id,
    ):

        for worker in self.workers:

            if worker["id"] == worker_id:

                worker["status"] = "idle"

                return True

        return False

    def recover_workers(
        self,
    ):

        recovered = 0

        for worker in self.workers:

            if worker["status"] != "failed":
                continue

            worker["status"] = "idle"

            recovered += 1

        return recovered


    def metrics(
        self,
    ):

        health = self.health()

        return {
            "workers": health["workers"],
            "busy": health["busy"],
            "idle": health["idle"],
            "healthy": health["healthy"],
            "utilization": health["utilization"],
            "jobs_processed": sum(
                w["jobs"]
                for w in self.workers
            ),
        }


worker_pool = WorkerPool()


scheduler = Scheduler()
