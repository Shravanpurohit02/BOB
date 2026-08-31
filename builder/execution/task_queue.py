from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class QueueTask:
    id: str
    title: str
    objective: str
    priority: int = 0
    dependencies: list[str] = field(default_factory=list)
    completed: bool = False
    failed: bool = False


class ExecutionQueue:
    def __init__(self):
        self._tasks: list[QueueTask] = []

    def add(self, task: QueueTask):
        self._tasks.append(task)

    def extend(self, tasks):
        self._tasks.extend(tasks)

    def pending(self):
        return [t for t in self._tasks if not t.completed and not t.failed]

    def ready(self):
        completed = {t.id for t in self._tasks if t.completed}

        return [
            t for t in self.pending() if all(dep in completed for dep in t.dependencies)
        ]

    def complete(self, task_id: str):
        for t in self._tasks:
            if t.id == task_id:
                t.completed = True
                return

    def fail(self, task_id: str):
        for t in self._tasks:
            if t.id == task_id:
                t.failed = True
                return

    @property
    def tasks(self):
        return list(self._tasks)


engine = ExecutionQueue()
