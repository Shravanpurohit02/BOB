import json
from pathlib import Path

TASK_FILE = Path(".builder/state/tasks.json")
QUEUE_FILE = Path(".builder/state/queue.json")


class RecoveryManager:

    def recover(self):

        if not TASK_FILE.exists():
            return 0

        tasks = json.loads(TASK_FILE.read_text(encoding="utf-8"))

        queue = []
        recovered = 0

        for task in tasks:

            if task.get("status") == "running":
                task["status"] = "pending"
                recovered += 1

            if task.get("status") == "pending":
                queue.append(task["id"])

        TASK_FILE.write_text(
            json.dumps(tasks, indent=2),
            encoding="utf-8",
        )

        QUEUE_FILE.write_text(
            json.dumps(queue, indent=2),
            encoding="utf-8",
        )

        return recovered


recovery = RecoveryManager()
