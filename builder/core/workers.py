from builder.models.worker import Worker

class WorkerPool:

    def __init__(self):
        self._workers = {}

    def create(self, name: str, agent: str):
        worker = Worker(
            name=name,
            agent=agent,
        )
        self._workers[name] = worker
        return worker

    def get(self, name: str):
        return self._workers.get(name)

    def start(self, name: str, task: str):
        worker = self._workers[name]
        worker.status = "running"
        worker.current_task = task
        return worker

    def stop(self, name: str):
        worker = self._workers[name]
        worker.status = "idle"
        worker.current_task = None
        return worker

    def all(self):
        return list(self._workers.values())

workers = WorkerPool()
