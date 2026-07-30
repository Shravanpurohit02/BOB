from __future__ import annotations

from dataclasses import asdict

from .models import (
    ExecutionCheckpoint,
    ExecutionSnapshot,
)


class SnapshotSerializer:

    def dumps(
        self,
        snapshot: ExecutionSnapshot,
    ) -> dict:

        return asdict(snapshot)

    def loads(
        self,
        data: dict,
    ) -> ExecutionSnapshot:

        checkpoints = [
            ExecutionCheckpoint(**cp)
            for cp in data.pop(
                "checkpoints",
                [],
            )
        ]

        snapshot = ExecutionSnapshot(**data)

        snapshot.checkpoints.extend(
            checkpoints
        )

        return snapshot


serializer = SnapshotSerializer()
