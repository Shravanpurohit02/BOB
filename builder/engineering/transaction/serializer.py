from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path


class TransactionSerializer:

    def _convert(self, obj):

        if is_dataclass(obj):
            return self._convert(asdict(obj))

        if isinstance(obj, dict):
            return {
                k: self._convert(v)
                for k, v in obj.items()
            }

        if isinstance(obj, (list, tuple)):
            return [
                self._convert(v)
                for v in obj
            ]

        if isinstance(obj, Path):
            return str(obj)

        return obj

    def dumps(
        self,
        obj,
        *,
        indent: int = 2,
    ) -> str:

        return json.dumps(
            self._convert(obj),
            indent=indent,
            ensure_ascii=False,
        )

    def dump(
        self,
        obj,
        path,
    ):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.dumps(obj),
            encoding="utf-8",
        )

        return path

    def loads(
        self,
        text: str,
    ):

        return json.loads(text)

    def load(
        self,
        path,
    ):

        path = Path(path)

        return self.loads(
            path.read_text(
                encoding="utf-8",
            )
        )


serializer = TransactionSerializer()
