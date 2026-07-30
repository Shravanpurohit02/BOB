from __future__ import annotations

from datetime import UTC, datetime

from .models import ExecutionSnapshot
from .storage import storage


class SnapshotEngine:

    def create(
        self,
        *,
        transaction_id: str = "",
        execution_id: str = "",
        objective: str = "",
        workspace: str = ".",
    ):

        snapshot = ExecutionSnapshot(
            transaction_id=transaction_id,
            execution_id=execution_id,
            objective=objective,
            workspace=workspace,
        )

        storage.save(snapshot)

        return snapshot

    def save(
        self,
        snapshot,
    ):

        snapshot.updated_at = (
            datetime.now(UTC).isoformat()
        )

        storage.save(snapshot)

        return snapshot

    def load(
        self,
        snapshot_id,
    ):

        return storage.load(snapshot_id)

    def checkpoint(
        self,
        snapshot,
        stage,
    ):

        snapshot.checkpoint(stage)

        self.save(snapshot)

        return snapshot

    def complete_stage(
        self,
        snapshot,
        stage,
    ):

        snapshot.complete_stage(stage)

        self.save(snapshot)

        return snapshot

    def commit(
        self,
        snapshot,
    ):

        snapshot.status = "completed"

        snapshot.completed_at = (
            datetime.now(UTC).isoformat()
        )

        self.save(snapshot)

        return snapshot

    def fail(
        self,
        snapshot,
    ):

        snapshot.status = "failed"

        self.save(snapshot)

        return snapshot

    def latest(self):

        return storage.latest()

    def list(self):

        return storage.list()

    def delete(
        self,
        snapshot_id,
    ):

        return storage.delete(snapshot_id)


engine = SnapshotEngine()
