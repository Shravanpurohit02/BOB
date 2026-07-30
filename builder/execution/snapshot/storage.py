from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .serializer import serializer


STATE = (
    Path.cwd()
    / ".builder"
    / "state"
    / "execution"
    / "snapshots"
)


class SnapshotStorage:

    def __init__(self):

        STATE.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _path(
        self,
        snapshot_id: str,
    ) -> Path:

        return STATE / f"{snapshot_id}.json"

    def exists(
        self,
        snapshot_id: str,
    ) -> bool:

        return self._path(snapshot_id).exists()

    def save(
        self,
        snapshot,
    ) -> Path:

        target = self._path(snapshot.id)

        payload = serializer.dumps(snapshot)

        with tempfile.NamedTemporaryFile(
            "w",
            dir=STATE,
            delete=False,
            encoding="utf-8",
        ) as tmp:

            json.dump(
                payload,
                tmp,
                indent=2,
                ensure_ascii=False,
            )

            tmp.flush()

            temp_path = Path(tmp.name)

        temp_path.replace(target)

        snapshot.metadata.setdefault(
            "committed_at",
            __import__("datetime").datetime.now(
                __import__("datetime").UTC
            ).isoformat(),
        )

        return target

    def load(
        self,
        snapshot_id: str,
    ):

        target = self._path(snapshot_id)

        if not target.exists():
            return None

        return serializer.loads(
            json.loads(
                target.read_text(
                    encoding="utf-8",
                )
            )
        )

    def delete(
        self,
        snapshot_id: str,
    ) -> bool:

        target = self._path(snapshot_id)

        if not target.exists():
            return False

        target.unlink()

        return True

    def list(self):

        result = []

        for file in sorted(
            STATE.glob("*.json")
        ):

            try:

                result.append(
                    serializer.loads(
                        json.loads(
                            file.read_text(
                                encoding="utf-8",
                            )
                        )
                    )

                )

            except Exception:
                continue

        return result

    def latest(self):

        files = sorted(
            STATE.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        if not files:
            return None

        return serializer.loads(
            json.loads(
                files[0].read_text(
                    encoding="utf-8",
                )
            )
        )


storage = SnapshotStorage()
