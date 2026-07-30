from datetime import datetime
from pathlib import Path

from builder.review.models import ReviewTask
from builder.review.storage import storage
from builder.self_improvement.models import Improvement


class ReviewEngine:

    def list(self):
        return storage.load()

    def submit(self, improvement):

        tasks = storage.load()

        for task in tasks:

            if (
                task.target == improvement.target
                and task.issue == improvement.issue
                and task.status in (
                    "pending",
                    "approved",
                )
            ):
                return task

        task = ReviewTask(
            target=improvement.target,
            issue=improvement.issue,
            proposal=improvement.proposal,
            priority=improvement.priority,
        )

        tasks.append(task)

        storage.save(tasks)

        return task

    def approve(
        self,
        task_id: str,
        reviewer: str = "builder",
    ):

        tasks = storage.load()

        for task in tasks:

            if task.id == task_id:

                task.status = "approved"
                task.reviewer = reviewer
                task.reviewed_at = (
                    datetime.utcnow().isoformat()
                )

                storage.save(tasks)

                return task

        return None

    def reject(
        self,
        task_id: str,
        reviewer: str = "builder",
    ):

        tasks = storage.load()

        for task in tasks:

            if task.id == task_id:

                task.status = "rejected"
                task.reviewer = reviewer
                task.reviewed_at = (
                    datetime.utcnow().isoformat()
                )

                storage.save(tasks)

                return task

        return None

    #
    # High-level API
    #

    def review(
        self,
        *,
        workspace: str,
        objective: str,
        priority: int = 1,
        transaction=None,
    ):

        improvement = Improvement(
            target=str(Path(workspace).resolve()),
            issue=objective,
            proposal=objective,
            priority=priority,
        )

        task = self.submit(improvement)

        if (
            transaction is not None
            and getattr(transaction, "transaction", None) is not None
        ):
            try:
                task.metadata["transaction"] = transaction.id
                storage.save(storage.load())
            except Exception:
                pass

        return task


engine = ReviewEngine()
