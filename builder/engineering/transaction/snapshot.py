from __future__ import annotations

import hashlib
from datetime import UTC, datetime
import shutil
from pathlib import Path


SNAPSHOT_ROOT = (
    Path.cwd()
    / ".builder"
    / "state"
    / "transactions"
    / "snapshots"
)


class SnapshotEngine:

    def _dir(self, transaction_id: str) -> Path:
        path = SNAPSHOT_ROOT / transaction_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _name(self, file: Path) -> str:
        return hashlib.sha256(
            str(file).encode("utf-8")
        ).hexdigest()

    def snapshot(
        self,
        transaction_id: str,
        path: str,
    ) -> Path | None:

        src = Path(path)

        if not src.exists():
            return None

        target = self._dir(transaction_id) / self._name(src)

        shutil.copy2(src, target)

        digest = hashlib.sha256(
            src.read_bytes()
        ).hexdigest()

        return {
            "path": str(src.resolve()),
            "snapshot": str(target.resolve()),
            "sha256": digest,
            "size": src.stat().st_size,
            "created_at": datetime.now(UTC).isoformat(),
        }

    def restore(
        self,
        manifest: dict,
    ) -> bool:

        snap = Path(
            manifest["snapshot"]
        )

        dst = Path(
            manifest["path"]
        )

        if not snap.exists():
            return False

        dst.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            snap,
            dst,
        )

        return True

    def delete(
        self,
        transaction_id: str,
    ):

        folder = self._dir(transaction_id)

        if folder.exists():
            shutil.rmtree(folder)

    def exists(
        self,
        transaction_id: str,
        path: str,
    ) -> bool:

        return (
            self._dir(transaction_id)
            / self._name(Path(path))
        ).exists()


    def verify(
        self,
        manifest: dict,
    ) -> dict:

        snap = Path(
            manifest["snapshot"]
        )

        if not snap.exists():
            return {
                "valid": False,
                "reason": "snapshot_missing",
            }

        digest = hashlib.sha256(
            snap.read_bytes()
        ).hexdigest()

        if digest != manifest["sha256"]:
            return {
                "valid": False,
                "reason": "hash_mismatch",
            }

        return {
            "valid": True,
            "reason": "",
        }



engine = SnapshotEngine()
