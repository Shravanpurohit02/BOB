from __future__ import annotations

import json
import tempfile
from pathlib import Path


STATE = (
    Path.cwd()
    / ".builder"
    / "state"
    / "transactions"
)


class TransactionStorage:

    def __init__(self):
        STATE.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _path(self, transaction_id: str) -> Path:
        return STATE / f"{transaction_id}.json"

    def exists(self, transaction_id: str) -> bool:
        return self._path(transaction_id).exists()

    def save(self, transaction: dict) -> Path:

        target = self._path(transaction["id"])

        with tempfile.NamedTemporaryFile(
            "w",
            dir=STATE,
            delete=False,
            encoding="utf-8",
        ) as tmp:

            json.dump(
                transaction,
                tmp,
                indent=2,
                ensure_ascii=False,
            )

            tmp.flush()

            temp_path = Path(tmp.name)

        temp_path.replace(target)

        return target

    def load(self, transaction_id: str):

        target = self._path(transaction_id)

        if not target.exists():
            return None

        return json.loads(
            target.read_text(
                encoding="utf-8",
            )
        )

    def delete(self, transaction_id: str) -> bool:

        target = self._path(transaction_id)

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
                    json.loads(
                        file.read_text(
                            encoding="utf-8",
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

        return json.loads(
            files[0].read_text(
                encoding="utf-8",
            )
        )


storage = TransactionStorage()
