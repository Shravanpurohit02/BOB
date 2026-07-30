import json
from collections import deque
from dataclasses import asdict
from pathlib import Path

from builder.models.task import Task
from builder.autonomous_runtime import engine as runtime_engine

TASK_FILE = Path(".builder/state/tasks.json")
QUEUE_FILE = Path(".builder/state/queue.json")


class TaskQueue:

    def __init__(self):
        self._queue = deque()
        self._load()

    def _load(self):
        if TASK_FILE.exists():
            data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
            self._queue = deque(Task(**t) for t in data)

    def _save(self):
        TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
        TASK_FILE.write_text(
            json.dumps(
                [asdict(t) for t in self._queue],
                indent=2,
            ),
            encoding="utf-8",
        )

    def submit(self, name: str, **payload):

        task = Task(
            name=name,
            payload=payload,
        )

        task.status = "running"

        self._queue.append(task)
        self._save()

        queue = []

        if QUEUE_FILE.exists():
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))

        queue.append(task.id)

        QUEUE_FILE.write_text(
            json.dumps(queue, indent=2),
            encoding="utf-8",
        )

        result = runtime_engine.execute(
            name,
            str(Path.cwd()),
        )

        task.status = (
            "completed"
            if result.success
            else "failed"
        )

        if QUEUE_FILE.exists():
            queue = json.loads(
                QUEUE_FILE.read_text(
                    encoding="utf-8"
                )
            )

            queue = [
                q for q in queue
                if q != task.id
            ]

            QUEUE_FILE.write_text(
                json.dumps(
                    queue,
                    indent=2,
                ),
                encoding="utf-8",
            )

        task.payload["runtime"] = {
            "success": result.success,
            "attempts": result.context.attempts,
            "stages": result.history,
        }

        self._save()

        return task

    def next(self):
        for task in self._queue:
            if task.status in ("pending","running"):
                return task
        return None


    def queue_size(self):

        if not QUEUE_FILE.exists():
            return 0

        return len(
            json.loads(
                QUEUE_FILE.read_text(
                    encoding="utf-8"
                )
            )
        )

    def __len__(self):
        return self.queue_size()


queue = TaskQueue()
