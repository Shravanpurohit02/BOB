from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import CodeAsset
from .store import CodeLibraryStore


@dataclass(slots=True, frozen=True)
class CodeLibraryCatalogEntry:
    asset_id: str
    stable_id: str
    asset_type: str
    name: str
    language: str
    framework: str
    runtime: str
    version: str
    lifecycle: str
    tags: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    parent_id: str = ""
    fingerprint: str = ""
    success_rate: float = 0.0


@dataclass(slots=True, frozen=True)
class CodeLibraryCatalog:
    total: int
    entries: tuple[CodeLibraryCatalogEntry, ...]
    by_type: dict[str, int] = field(default_factory=dict)
    by_language: dict[str, int] = field(default_factory=dict)
    by_framework: dict[str, int] = field(default_factory=dict)
    by_runtime: dict[str, int] = field(default_factory=dict)
    by_lifecycle: dict[str, int] = field(default_factory=dict)
    by_tag: dict[str, int] = field(default_factory=dict)
    by_capability: dict[str, int] = field(default_factory=dict)


class CodeLibraryCatalogEngine:
    """
    Deterministic catalog and organization layer for the BOB Code Library.

    The catalog is derived from canonical CodeAsset records stored by
    CodeLibraryStore. It does not create a second source of truth.

    CL-2 responsibilities:
    - enumerate canonical assets;
    - normalize catalog dimensions;
    - provide deterministic filtering;
    - organize assets by type, technology and lifecycle;
    - expose tags, capabilities and dependencies;
    - preserve asset identity and fingerprints;
    - provide metadata suitable for later retrieval phases.
    """

    def __init__(
        self,
        store: CodeLibraryStore | None = None,
    ) -> None:
        self.store = store or CodeLibraryStore()

    @staticmethod
    def _normalize(value: str) -> str:
        return str(value or "").strip().lower()

    @classmethod
    def _values(
        cls,
        values: Iterable[str],
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    cls._normalize(value)
                    for value in values
                    if cls._normalize(value)
                }
            )
        )

    @classmethod
    def entry(
        cls,
        asset: CodeAsset,
    ) -> CodeLibraryCatalogEntry:
        return CodeLibraryCatalogEntry(
            asset_id=asset.id,
            stable_id=asset.stable_id,
            asset_type=cls._normalize(asset.asset_type),
            name=asset.name,
            language=cls._normalize(asset.language),
            framework=cls._normalize(asset.framework),
            runtime=cls._normalize(asset.runtime),
            version=asset.version,
            lifecycle=cls._normalize(asset.lifecycle),
            tags=cls._values(asset.tags),
            capabilities=cls._values(asset.capabilities),
            dependencies=cls._values(asset.dependencies),
            parent_id=asset.parent_id,
            fingerprint=asset.fingerprint,
            success_rate=asset.success_rate,
        )

    def catalog(
        self,
        assets: Iterable[CodeAsset] | None = None,
    ) -> CodeLibraryCatalog:
        source = (
            list(assets)
            if assets is not None
            else self.store.all()
        )

        entries = tuple(
            sorted(
                (
                    self.entry(asset)
                    for asset in source
                ),
                key=lambda item: (
                    item.asset_type,
                    item.name.lower(),
                    item.asset_id,
                ),
            )
        )

        return CodeLibraryCatalog(
            total=len(entries),
            entries=entries,
            by_type=self._count(
                entry.asset_type for entry in entries
            ),
            by_language=self._count(
                entry.language for entry in entries
            ),
            by_framework=self._count(
                entry.framework for entry in entries
            ),
            by_runtime=self._count(
                entry.runtime for entry in entries
            ),
            by_lifecycle=self._count(
                entry.lifecycle for entry in entries
            ),
            by_tag=self._count_many(
                entry.tags for entry in entries
            ),
            by_capability=self._count_many(
                entry.capabilities for entry in entries
            ),
        )

    @staticmethod
    def _count(
        values: Iterable[str],
    ) -> dict[str, int]:
        result: dict[str, int] = {}

        for value in values:
            if not value:
                continue

            result[value] = result.get(value, 0) + 1

        return dict(sorted(result.items()))

    @classmethod
    def _count_many(
        cls,
        values: Iterable[Iterable[str]],
    ) -> dict[str, int]:
        flattened = (
            item
            for group in values
            for item in group
        )

        return cls._count(flattened)

    def list(
        self,
        *,
        asset_type: str | None = None,
        language: str | None = None,
        framework: str | None = None,
        runtime: str | None = None,
        lifecycle: str | None = None,
        tag: str | None = None,
        capability: str | None = None,
        dependency: str | None = None,
        parent_id: str | None = None,
        assets: Iterable[CodeAsset] | None = None,
    ) -> list[CodeAsset]:
        source = (
            list(assets)
            if assets is not None
            else self.store.all()
        )

        asset_type = self._normalize(asset_type or "")
        language = self._normalize(language or "")
        framework = self._normalize(framework or "")
        runtime = self._normalize(runtime or "")
        lifecycle = self._normalize(lifecycle or "")
        tag = self._normalize(tag or "")
        capability = self._normalize(capability or "")
        dependency = self._normalize(dependency or "")
        parent_id = str(parent_id or "").strip()

        result: list[CodeAsset] = []

        for asset in source:
            if asset_type and self._normalize(
                asset.asset_type
            ) != asset_type:
                continue

            if language and self._normalize(
                asset.language
            ) != language:
                continue

            if framework and self._normalize(
                asset.framework
            ) != framework:
                continue

            if runtime and self._normalize(
                asset.runtime
            ) != runtime:
                continue

            if lifecycle and self._normalize(
                asset.lifecycle
            ) != lifecycle:
                continue

            if tag and tag not in {
                self._normalize(value)
                for value in asset.tags
            }:
                continue

            if capability and capability not in {
                self._normalize(value)
                for value in asset.capabilities
            }:
                continue

            if dependency and dependency not in {
                self._normalize(value)
                for value in asset.dependencies
            }:
                continue

            if parent_id and asset.parent_id != parent_id:
                continue

            result.append(asset)

        return sorted(
            result,
            key=lambda asset: (
                self._normalize(asset.asset_type),
                asset.name.lower(),
                asset.id,
            ),
        )

    def get(
        self,
        asset_id: str,
    ) -> CodeLibraryCatalogEntry | None:
        asset = self.store.get(asset_id)

        if asset is None:
            return None

        return self.entry(asset)

    def categories(self) -> dict[str, dict[str, int]]:
        result = self.catalog()

        return {
            "asset_type": dict(result.by_type),
            "language": dict(result.by_language),
            "framework": dict(result.by_framework),
            "runtime": dict(result.by_runtime),
            "lifecycle": dict(result.by_lifecycle),
            "tag": dict(result.by_tag),
            "capability": dict(result.by_capability),
        }


catalog = CodeLibraryCatalogEngine()


__all__ = (
    "CodeLibraryCatalog",
    "CodeLibraryCatalogEngine",
    "CodeLibraryCatalogEntry",
    "catalog",
)
