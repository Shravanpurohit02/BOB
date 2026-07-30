from __future__ import annotations

import time
from datetime import UTC, datetime

from .events import (
    CHECKPOINT,
    ERROR,
    EXECUTION,
    INFO,
    RECOVERY,
    RUNTIME,
    TESTING,
    VALIDATION,
)
from .models import EngineeringTransaction
from .recovery import recovery
from .serializer import serializer
from .storage import storage
from .snapshot import engine as snapshots
from builder.events import engine as events


class TransactionEngine:

    def begin(
        self,
        objective: str,
        workspace: str = "",
    ):

        tx = EngineeringTransaction(
            objective=objective,
            workspace=workspace,
            status="running",
        )

        self.add_event(
            tx,
            INFO,
            "transaction",
            "Transaction started",
        )

        events.publish(
            "transaction.started",
            source="transaction",
            payload={"id": tx.id},
        )

        self.save(tx)

        return tx

    def save(self, tx):

        storage.save(
            serializer.loads(
                serializer.dumps(tx)
            )
        )

        return tx

    def load(self, transaction_id):

        return storage.load(transaction_id)

    def checkpoint(
        self,
        tx,
        message="Checkpoint",
    ):

        tx.metadata["last_checkpoint"] = (
            datetime.now(UTC).isoformat()
        )

        self.add_event(
            tx,
            CHECKPOINT,
            "checkpoint",
            message,
        )

        self.save(tx)

        return tx

    def add_stage(
        self,
        tx,
        stage,
    ):

        if tx.stage(stage) is None:
            tx.add_stage(stage)

        return tx.stage(stage)

    def start_stage(
        self,
        tx,
        stage,
    ):

        s = self.add_stage(
            tx,
            stage,
        )

        s.status = "running"
        s.started_at = (
            datetime.now(UTC).isoformat()
        )

        s.metadata["_timer"] = (
            time.perf_counter()
        )

        events.publish(
            "transaction.stage.started",
            source="transaction",
            payload={
                "transaction": tx.id,
                "stage": stage,
            },
        )

        self.save(tx)

        return s

    def finish_stage(
        self,
        tx,
        stage,
        status="completed",
    ):

        s = self.add_stage(
            tx,
            stage,
        )

        s.status = status
        s.completed_at = (
            datetime.now(UTC).isoformat()
        )

        timer = s.metadata.pop(
            "_timer",
            None,
        )

        if timer is not None:
            s.duration = round(
                time.perf_counter() - timer,
                6,
            )

        events.publish(
            "transaction.stage.completed",
            source="transaction",
            payload={
                "transaction": tx.id,
                "stage": stage,
                "status": status,
            },
        )

        self.save(tx)

        return s

    def add_event(
        self,
        tx,
        level,
        source,
        message,
        metadata=None,
    ):

        tx.add_event(
            str(level),
            source,
            message,
            metadata,
        )

        return tx.events[-1]

    def attach_changeset(
        self,
        tx,
        changeset,
    ):

        tx.changeset_id = getattr(
            changeset,
            "id",
            str(changeset),
        )

        self.save(tx)

    def attach_execution(
        self,
        tx,
        result,
    ):

        tx.execution_result = result

        self.add_event(
            tx,
            EXECUTION,
            "execution",
            "Execution attached",
        )

        self.save(tx)

    def attach_runtime(
        self,
        tx,
        result,
    ):

        tx.runtime_result = result

        self.add_event(
            tx,
            RUNTIME,
            "runtime",
            "Runtime attached",
        )

        self.save(tx)

    def attach_validation(
        self,
        tx,
        validation,
    ):

        tx.validation = validation

        self.add_event(
            tx,
            VALIDATION,
            "validation",
            "Validation completed",
        )

        self.save(tx)

    def attach_testing(
        self,
        tx,
        testing,
    ):

        tx.testing = testing

        self.add_event(
            tx,
            TESTING,
            "testing",
            "Testing completed",
        )

        self.save(tx)

    def attach_artifact(
        self,
        tx,
        artifact,
    ):

        if artifact not in tx.artifacts:
            tx.artifacts.append(artifact)

        self.save(tx)

    

    def snapshot_file(
        self,
        tx,
        path,
    ):

        snap = snapshots.snapshot(
            tx.id,
            path,
        )

        if snap is not None:

            tx.metadata.setdefault(
                "snapshots",
                [],
            ).append(snap)

            if path not in tx.artifacts:
                tx.artifacts.append(path)

        self.add_event(
            tx,
            INFO,
            "snapshot",
            f"Snapshot created: {path}",
        )

        self.save(tx)

    def stage_completed(
        self,
        tx,
        stage,
    ) -> bool:

        s = tx.stage(stage)

        return (
            s is not None
            and s.status == "completed"
        )



    def commit(
            self,
            tx,
        ):

            tx.status = "completed"
            tx.completed_at = (
                datetime.now(UTC).isoformat()
            )

            self.add_event(
                tx,
                INFO,
                "transaction",
                "Committed",
            )

            events.publish(
                "transaction.completed",
                source="transaction",
                payload={"id": tx.id},
            )

            self.save(tx)

    def rollback(
        self,
        tx,
        reason="",
    ):

        for manifest in tx.metadata.get(
            "snapshots",
            [],
        ):
            try:

                report = snapshots.verify(
                    manifest,
                )

                if report["valid"]:
                    snapshots.restore(
                        manifest,
                    )
                else:
                    self.add_event(
                        tx,
                        ERROR,
                        "snapshot",
                        "Snapshot verification failed",
                        report,
                    )

            except Exception as exc:
                self.add_event(
                    tx,
                    ERROR,
                    "snapshot",
                    str(exc),
                )

        tx.status = "rolled_back"
        tx.rollback_required = False

        self.add_event(
            tx,
            RECOVERY,
            "rollback",
            reason or "Rollback completed",
        )

        self.save(tx)

    def fail(
        self,
        tx,
        reason="",
    ):

        tx.status = "failed"
        tx.rollback_required = True

        self.add_event(
            tx,
            ERROR,
            "transaction",
            reason or "Transaction failed",
        )

        self.save(tx)

    def close(
        self,
        tx,
    ):

        self.save(tx)

        return tx

    def latest_incomplete(self):

        return recovery.latest_incomplete()

    def resume_latest(self):

        return recovery.resume_latest()


    def recover_active(self):

        recovered = []

        for tx in storage.list():

            if tx.get("status") != "running":
                continue

            tx["status"] = "failed"

            tx["rollback_required"] = True

            tx.setdefault(
                "metadata",
                {},
            )

            tx["metadata"]["crash_recovered"] = True

            tx["metadata"]["recovery_reason"] = (
                "Unexpected process termination"
            )

            storage.save(tx)

            recovered.append(tx["id"])

        return recovered


engine = TransactionEngine()
