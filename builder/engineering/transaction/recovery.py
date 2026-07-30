from __future__ import annotations

from datetime import UTC, datetime

from .storage import storage


class TransactionRecovery:

    ACTIVE = {
        "created",
        "running",
        "checkpoint",
    }

    TERMINAL = {
        "completed",
        "failed",
        "rolled_back",
        "abandoned",
    }

    def list(self):
        return storage.list()

    def find_incomplete(self):

        return [
            tx
            for tx in storage.list()
            if tx.get("status") in self.ACTIVE
        ]

    def latest_incomplete(self):

        txs = self.find_incomplete()

        if not txs:
            return None

        txs.sort(
            key=lambda t: t.get(
                "started_at",
                "",
            ),
            reverse=True,
        )

        return txs[0]

    def resume_latest(self):

        tx = self.latest_incomplete()

        if tx is None:
            return None

        tx.setdefault(
            "metadata",
            {},
        )

        tx["metadata"]["resumed"] = True
        tx["metadata"]["resumed_at"] = (
            datetime.now(UTC).isoformat()
        )

        storage.save(tx)

        return tx

    def validate_transaction(
        self,
        tx,
    ):

        required = (
            "id",
            "objective",
            "status",
            "started_at",
            "metadata",
            "events",
            "stages",
            "artifacts",
        )

        missing = [
            field
            for field in required
            if field not in tx
        ]

        return {
            "valid": len(missing) == 0,
            "missing": missing,
        }

    def repair_metadata(
        self,
        tx,
    ):

        tx.setdefault("metadata", {})
        tx.setdefault("events", [])
        tx.setdefault("stages", [])
        tx.setdefault("artifacts", [])
        tx.setdefault("validation", {})
        tx.setdefault("testing", {})
        tx.setdefault("rollback_required", False)

        return tx

    def mark_abandoned(
        self,
        transaction_id,
    ):

        tx = storage.load(transaction_id)

        if tx is None:
            return None

        tx["status"] = "abandoned"

        tx.setdefault(
            "metadata",
            {},
        )

        tx["metadata"]["abandoned_at"] = (
            datetime.now(UTC).isoformat()
        )

        storage.save(tx)

        return tx

    def recover(
        self,
        transaction_id,
    ):

        tx = storage.load(transaction_id)

        if tx is None:
            return None

        tx = self.repair_metadata(tx)

        report = self.validate_transaction(tx)

        tx["metadata"]["recovery"] = report

        storage.save(tx)

        return tx


recovery = TransactionRecovery()
