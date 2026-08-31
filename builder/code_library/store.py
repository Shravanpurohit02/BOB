from __future__ import annotations

import json
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path

from builder.config import settings

from .models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetProvenance,
    CodeAssetRelationship,
    CodeAssetUsage,
    CodeAssetVersion,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CodeLibraryStore:
    """
    Persistent JSON-backed Code Library store.

    One asset is stored per JSON document. Writes are atomic so
    interrupted writes cannot replace an existing valid asset
    with a partial document.
    """

    def __init__(
        self,
        root: Path | None = None,
    ) -> None:
        self.root = (
            Path(root)
            if root is not None
            else (
                settings.resolve_memory_directory()
                / "code_library"
            )
        )
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _file(
        self,
        asset_id: str,
    ) -> Path:
        return self.root / f"{asset_id}.json"

    def save(
        self,
        asset: CodeAsset,
    ) -> CodeAsset:
        asset.updated_at = _now()

        target = self._file(asset.id)
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(
                asset.as_dict(),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        temporary.replace(target)

        return asset

    def get(
        self,
        asset_id: str,
    ) -> CodeAsset | None:
        target = self._file(asset_id)

        if not target.exists():
            return None

        try:
            data = json.loads(
                target.read_text(
                    encoding="utf-8",
                )
            )
        except (OSError, ValueError):
            return None

        return self._from_dict(data)

    def all(self) -> list[CodeAsset]:
        assets: list[CodeAsset] = []

        for target in sorted(
            self.root.glob("*.json")
        ):
            asset = self.get(target.stem)

            if asset is not None:
                assets.append(asset)

        return assets

    def delete(
        self,
        asset_id: str,
    ) -> bool:
        target = self._file(asset_id)

        if not target.exists():
            return False

        target.unlink()
        return True

    def exists(
        self,
        asset_id: str,
    ) -> bool:
        return self._file(asset_id).exists()

    def count(self) -> int:
        return len(
            list(self.root.glob("*.json"))
        )

    @staticmethod
    def _from_dict(
        data: dict,
    ) -> CodeAsset:
        files = [
            CodeAssetFile(**item)
            for item in data.pop(
                "files",
                [],
            )
        ]

        relationships = [
            CodeAssetRelationship(**item)
            for item in data.pop(
                "relationships",
                [],
            )
        ]

        provenance_data = data.pop(
            "provenance",
            {},
        )
        provenance = CodeAssetProvenance(
            **provenance_data
        )

        versions = [
            CodeAssetVersion(**item)
            for item in data.pop(
                "versions",
                [],
            )
        ]

        usage = CodeAssetUsage(
            **data.pop(
                "usage",
                {},
            )
        )

        allowed = {
            item.name
            for item in fields(CodeAsset)
        }

        cleaned = {
            key: value
            for key, value in data.items()
            if key in allowed
        }

        return CodeAsset(
            **cleaned,
            files=files,
            relationships=relationships,
            provenance=provenance,
            versions=versions,
            usage=usage,
        )


__all__ = (
    "CodeLibraryStore",
)
