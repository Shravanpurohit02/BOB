from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class LocalStorageContext:
    root: str
    namespace: str = "code_library"
    version: int = 1

    def __post_init__(self) -> None:
        if not self.root.strip():
            raise ValueError("root must not be empty")
        if not self.namespace.strip():
            raise ValueError("namespace must not be empty")
        if self.version < 1:
            raise ValueError("version must be positive")

    @property
    def root_path(self) -> Path:
        return Path(self.root).expanduser()

    @property
    def namespace_path(self) -> Path:
        return self.root_path / self.namespace

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "namespace": self.namespace,
            "version": self.version,
        }


@dataclass(frozen=True)
class LocalStorageRecord:
    key: str
    value: Any
    version: int = 1
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("key must not be empty")
        if self.version < 1:
            raise ValueError("version must be positive")

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "version": self.version,
            "metadata": dict(self.metadata or {}),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "LocalStorageRecord":
        if not isinstance(data, dict):
            raise TypeError("record data must be a dictionary")

        return cls(
            key=str(data["key"]),
            value=data.get("value"),
            version=int(data.get("version", 1)),
            metadata=dict(data.get("metadata") or {}),
        )


class CodeLibraryLocalStorage:
    """
    Small deterministic JSON-backed local storage layer.

    Storage is intentionally filesystem-only. It performs no network
    access and uses atomic replacement for writes.
    """

    FILE_NAME = "storage.json"
    TEMP_SUFFIX = ".tmp"

    def __init__(
        self,
        context: LocalStorageContext,
    ) -> None:
        self.context = context
        self.root = context.namespace_path
        self.file_path = self.root / self.FILE_NAME

    def initialize(self) -> Path:
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():
            self._write_payload(
                {
                    "version": self.context.version,
                    "records": {},
                }
            )

        return self.file_path

    def exists(self) -> bool:
        return self.file_path.is_file()

    def _read_payload(self) -> dict:
        if not self.exists():
            return {
                "version": self.context.version,
                "records": {},
            }

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid local storage JSON: {self.file_path}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Local storage payload must be a dictionary"
            )

        records = payload.get("records", {})

        if not isinstance(records, dict):
            raise ValueError(
                "Local storage records must be a dictionary"
            )

        return payload

    def _write_payload(
        self,
        payload: dict,
    ) -> None:
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        fd, temporary_name = tempfile.mkstemp(
            prefix=self.FILE_NAME,
            suffix=self.TEMP_SUFFIX,
            dir=str(self.root),
        )

        try:
            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    payload,
                    handle,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(
                temporary_name,
                self.file_path,
            )
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def put(
        self,
        key: str,
        value: Any,
        *,
        version: int = 1,
        metadata: dict | None = None,
    ) -> LocalStorageRecord:
        record = LocalStorageRecord(
            key=key,
            value=value,
            version=version,
            metadata=metadata,
        )

        payload = self._read_payload()
        records = dict(payload.get("records", {}))

        records[record.key] = record.to_dict()

        payload["version"] = self.context.version
        payload["records"] = records

        self._write_payload(payload)

        return record

    def put_many(
        self,
        records: Iterable[LocalStorageRecord],
    ) -> tuple[LocalStorageRecord, ...]:
        normalized = tuple(records)

        for record in normalized:
            if not isinstance(
                record,
                LocalStorageRecord,
            ):
                raise TypeError(
                    "records must contain LocalStorageRecord"
                )

        payload = self._read_payload()
        stored = dict(payload.get("records", {}))

        for record in normalized:
            stored[record.key] = record.to_dict()

        payload["version"] = self.context.version
        payload["records"] = stored

        self._write_payload(payload)

        return normalized

    def get(
        self,
        key: str,
    ) -> LocalStorageRecord | None:
        payload = self._read_payload()
        data = payload.get("records", {}).get(key)

        if data is None:
            return None

        return LocalStorageRecord.from_dict(data)

    def require(
        self,
        key: str,
    ) -> LocalStorageRecord:
        record = self.get(key)

        if record is None:
            raise ValueError(
                f"Local storage record not found: {key}"
            )

        return record

    def contains(
        self,
        key: str,
    ) -> bool:
        return self.get(key) is not None

    def remove(
        self,
        key: str,
    ) -> LocalStorageRecord | None:
        payload = self._read_payload()
        records = dict(payload.get("records", {}))

        data = records.pop(key, None)

        if data is None:
            return None

        payload["records"] = records
        payload["version"] = self.context.version

        self._write_payload(payload)

        return LocalStorageRecord.from_dict(data)

    def list_records(
        self,
    ) -> tuple[LocalStorageRecord, ...]:
        payload = self._read_payload()

        return tuple(
            LocalStorageRecord.from_dict(
                payload["records"][key]
            )
            for key in sorted(
                payload.get("records", {})
            )
        )

    def count(self) -> int:
        return len(self.list_records())

    def clear(self) -> None:
        payload = self._read_payload()

        payload["version"] = self.context.version
        payload["records"] = {}

        self._write_payload(payload)

    def delete_storage(self) -> bool:
        if not self.exists():
            return False

        self.file_path.unlink()
        return True

    def export_payload(self) -> dict:
        payload = self._read_payload()

        return {
            "version": int(
                payload.get(
                    "version",
                    self.context.version,
                )
            ),
            "records": {
                key: dict(value)
                for key, value in sorted(
                    payload.get(
                        "records",
                        {},
                    ).items()
                )
            },
        }

    def import_payload(
        self,
        payload: dict,
        *,
        replace: bool = False,
    ) -> tuple[LocalStorageRecord, ...]:
        if not isinstance(payload, dict):
            raise TypeError(
                "payload must be a dictionary"
            )

        incoming = payload.get("records", {})

        if not isinstance(incoming, dict):
            raise ValueError(
                "payload records must be a dictionary"
            )

        current = (
            {}
            if replace
            else self._read_payload().get(
                "records",
                {},
            )
        )

        normalized = []

        for key, data in incoming.items():
            record = LocalStorageRecord.from_dict(data)

            if record.key != key:
                raise ValueError(
                    "record key does not match payload key"
                )

            current[record.key] = record.to_dict()
            normalized.append(record)

        self._write_payload(
            {
                "version": self.context.version,
                "records": current,
            }
        )

        return tuple(normalized)

    def to_dict(self) -> dict:
        return {
            "context": self.context.to_dict(),
            "file_path": str(self.file_path),
            "exists": self.exists(),
            "count": self.count(),
            "records": [
                record.to_dict()
                for record in self.list_records()
            ],
        }


__all__ = [
    "LocalStorageContext",
    "LocalStorageRecord",
    "CodeLibraryLocalStorage",
]
