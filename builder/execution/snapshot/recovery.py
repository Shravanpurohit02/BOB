from __future__ import annotations

from datetime import UTC, datetime

from .storage import storage


class SnapshotRecovery:

    ACTIVE = {
        "created",
        "running",
    }

    TERMINAL = {
        "completed",
        "failed",
        "abandoned",
    }

    def list(self):
        return storage.list()

    def find_incomplete(self):

        return [
            s
            for s in storage.list()
            if s.status in self.ACTIVE
        ]

    def latest_incomplete(self):

        snapshots = self.find_incomplete()

        if not snapshots:
            return None

        snapshots.sort(
            key=lambda s: s.created_at,
            reverse=True,
        )

        return snapshots[0]

    def resume_latest(self):

        snapshot = self.latest_incomplete()

        if snapshot is None:
            return None

        snapshot.metadata["resumed"] = True

        snapshot.metadata["resumed_at"] = (
            datetime.now(UTC).isoformat()
        )

        storage.save(snapshot)

        return snapshot

    def validate(
        self,
        snapshot,
    ):

        required = (
            "id",
            "transaction_id",
            "execution_id",
            "status",
            "metadata",
            "checkpoints",
        )

        missing = [
            field
            for field in required
            if not hasattr(snapshot, field)
        ]

        return {
            "valid": len(missing) == 0,
            "missing": missing,
        }

    def repair(
        self,
        snapshot,
    ):

        if snapshot.metadata is None:
            snapshot.metadata = {}

        if snapshot.validation is None:
            snapshot.validation = {}

        if snapshot.testing is None:
            snapshot.testing = {}

        if snapshot.artifacts is None:
            snapshot.artifacts = []

        if snapshot.checkpoints is None:
            snapshot.checkpoints = []

        storage.save(snapshot)

        return snapshot

    def mark_abandoned(
        self,
        snapshot,
    ):

        snapshot.status = "abandoned"

        snapshot.metadata["abandoned_at"] = (
            datetime.now(UTC).isoformat()
        )

        storage.save(snapshot)

        return snapshot


    def next_stage(
        self,
        snapshot,
        pipeline,
    ):

        completed = {
            cp.stage
            for cp in snapshot.checkpoints
            if cp.status == "completed"
        }

        for stage in pipeline:
            if stage not in completed:
                return stage

        return None


    def garbage_collect(
        self,
        keep=25,
    ):

        snapshots = sorted(
            storage.list(),
            key=lambda s: s.updated_at,
            reverse=True,
        )

        removed = []

        for snapshot in snapshots[keep:]:

            if snapshot.status in self.ACTIVE:
                continue

            storage.delete(
                snapshot.id,
            )

            removed.append(
                snapshot.id,
            )

        return removed


recovery = SnapshotRecovery()
