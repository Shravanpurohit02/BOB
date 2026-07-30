from __future__ import annotations

from .engine import engine


class SnapshotManager:

    def create(
        self,
        **kwargs,
    ):
        return engine.create(**kwargs)

    def before_stage(
        self,
        snapshot,
        stage: str,
    ):

        snapshot.status = "running"

        engine.checkpoint(
            snapshot,
            stage,
        )

        return snapshot

    def after_stage(
        self,
        snapshot,
        stage: str,
        *,
        metadata: dict | None = None,
    ):

        engine.complete_stage(
            snapshot,
            stage,
        )

        if metadata:
            snapshot.metadata.setdefault(
                "stages",
                {},
            )[stage] = metadata

        engine.save(snapshot)

        return snapshot

    def fail_stage(
        self,
        snapshot,
        stage: str,
        reason: str = "",
    ):

        snapshot.metadata.setdefault(
            "failures",
            {},
        )[stage] = reason

        engine.fail(
            snapshot,
        )

        return snapshot

    def complete(
        self,
        snapshot,
    ):

        return engine.commit(
            snapshot,
        )


    def verify(
        self,
        snapshot,
    ):

        import hashlib
        import json

        payload = json.dumps(
            snapshot.metadata,
            sort_keys=True,
            default=str,
        ).encode("utf-8")

        digest = hashlib.sha256(
            payload
        ).hexdigest()

        expected = snapshot.metadata.get(
            "sha256",
        )

        if expected is None:

            snapshot.metadata["sha256"] = digest

            engine.save(snapshot)

            return {
                "valid": True,
                "created": True,
            }

        return {
            "valid": expected == digest,
            "created": False,
        }


    def acquire_lock(
        self,
        snapshot,
    ):

        if snapshot.metadata.get("locked", False):
            return False

        snapshot.metadata["locked"] = True

        snapshot.metadata["lock_owner"] = (
            snapshot.execution_id
        )

        engine.save(snapshot)

        return True

    def release_lock(
        self,
        snapshot,
    ):

        snapshot.metadata["locked"] = False

        snapshot.metadata.pop(
            "lock_owner",
            None,
        )

        engine.save(snapshot)

        return True


manager = SnapshotManager()
