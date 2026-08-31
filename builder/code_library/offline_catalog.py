from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class OfflineCatalogContext:
    platform: str = "android"
    language: str = ""
    framework: str = ""
    runtime: str = ""
    project_id: str = ""
    tags: tuple[str, ...] = ()

    def key(self) -> str:
        return "|".join(
            (
                self.platform.strip().lower(),
                self.language.strip().lower(),
                self.framework.strip().lower(),
                self.runtime.strip().lower(),
                self.project_id.strip(),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.tags
                        if value and value.strip()
                    )
                ),
            )
        )

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "project_id": self.project_id,
            "tags": list(self.tags),
            "context_key": self.key(),
        }


@dataclass(frozen=True)
class OfflineCatalogEntry:
    asset_id: str
    name: str
    asset_type: str
    version: str = "1.0.0"
    description: str = ""
    language: str = ""
    framework: str = ""
    runtime: str = ""
    tags: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    platforms: tuple[str, ...] = ("android",)
    offline_ready: bool = True
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id.strip():
            raise ValueError("asset_id must not be empty")
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.asset_type.strip():
            raise ValueError("asset_type must not be empty")

        object.__setattr__(
            self,
            "tags",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip().lower()
                        for value in self.tags
                        if value and value.strip()
                    )
                )
            ),
        )

        object.__setattr__(
            self,
            "dependencies",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip()
                        for value in self.dependencies
                        if value and value.strip()
                    )
                )
            ),
        )

        object.__setattr__(
            self,
            "platforms",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip().lower()
                        for value in self.platforms
                        if value and value.strip()
                    )
                )
            ),
        )

    def matches(
        self,
        *,
        query: str = "",
        asset_type: str = "",
        language: str = "",
        framework: str = "",
        runtime: str = "",
        platform: str = "",
        tags: Iterable[str] = (),
        offline_only: bool = False,
    ) -> bool:
        if query:
            needle = query.strip().lower()

            searchable = " ".join(
                (
                    self.asset_id,
                    self.name,
                    self.description,
                    self.language,
                    self.framework,
                    self.runtime,
                    " ".join(self.tags),
                )
            ).lower()

            if needle not in searchable:
                return False

        if asset_type and (
            self.asset_type.strip().lower()
            != asset_type.strip().lower()
        ):
            return False

        if language and (
            self.language.strip().lower()
            != language.strip().lower()
        ):
            return False

        if framework and (
            self.framework.strip().lower()
            != framework.strip().lower()
        ):
            return False

        if runtime and (
            self.runtime.strip().lower()
            != runtime.strip().lower()
        ):
            return False

        if platform and (
            platform.strip().lower()
            not in self.platforms
        ):
            return False

        requested_tags = {
            value.strip().lower()
            for value in tags
            if value and value.strip()
        }

        if requested_tags and not requested_tags.issubset(
            set(self.tags)
        ):
            return False

        if offline_only and not self.offline_ready:
            return False

        return True

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "name": self.name,
            "asset_type": self.asset_type,
            "version": self.version,
            "description": self.description,
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "tags": list(self.tags),
            "dependencies": list(self.dependencies),
            "platforms": list(self.platforms),
            "offline_ready": self.offline_ready,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class OfflineCatalogResult:
    entries: tuple[OfflineCatalogEntry, ...]
    query: str = ""
    total_count: int = 0
    returned_count: int = 0
    context_key: str = ""
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "entries": [
                entry.to_dict()
                for entry in self.entries
            ],
            "query": self.query,
            "total_count": self.total_count,
            "returned_count": self.returned_count,
            "context_key": self.context_key,
            "reasons": list(self.reasons),
        }


class CodeLibraryOfflineCatalog:
    """
    Deterministic in-memory offline catalog for Android Code Library
    assets.

    The catalog contains only local metadata and performs no network
    access. Entries are keyed by asset_id and duplicate registration
    replaces the existing entry deterministically.
    """

    def __init__(
        self,
        entries: Iterable[OfflineCatalogEntry] = (),
    ) -> None:
        self._entries: dict[
            str,
            OfflineCatalogEntry,
        ] = {}

        for entry in entries:
            self.register(entry)

    def register(
        self,
        entry: OfflineCatalogEntry,
    ) -> OfflineCatalogEntry:
        if not isinstance(
            entry,
            OfflineCatalogEntry,
        ):
            raise TypeError(
                "entry must be OfflineCatalogEntry"
            )

        self._entries[entry.asset_id] = entry
        return entry

    def register_many(
        self,
        entries: Iterable[OfflineCatalogEntry],
    ) -> tuple[OfflineCatalogEntry, ...]:
        registered = []

        for entry in entries:
            registered.append(
                self.register(entry)
            )

        return tuple(registered)

    def get(
        self,
        asset_id: str,
    ) -> OfflineCatalogEntry | None:
        return self._entries.get(asset_id)

    def require(
        self,
        asset_id: str,
    ) -> OfflineCatalogEntry:
        entry = self.get(asset_id)

        if entry is None:
            raise ValueError(
                f"Offline catalog asset not found: {asset_id}"
            )

        return entry

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return asset_id in self._entries

    def list_entries(
        self,
    ) -> tuple[OfflineCatalogEntry, ...]:
        return tuple(
            self._entries[asset_id]
            for asset_id in sorted(self._entries)
        )

    def search(
        self,
        query: str = "",
        *,
        asset_type: str = "",
        language: str = "",
        framework: str = "",
        runtime: str = "",
        platform: str = "",
        tags: Iterable[str] = (),
        offline_only: bool = False,
        context: OfflineCatalogContext | None = None,
        limit: int | None = None,
    ) -> OfflineCatalogResult:
        if limit is not None and limit < 1:
            raise ValueError(
                "limit must be positive"
            )

        entries = tuple(
            entry
            for entry in self.list_entries()
            if entry.matches(
                query=query,
                asset_type=asset_type,
                language=language,
                framework=framework,
                runtime=runtime,
                platform=platform,
                tags=tags,
                offline_only=offline_only,
            )
        )

        returned = (
            entries
            if limit is None
            else entries[:limit]
        )

        reasons = []

        if query:
            reasons.append("query_applied")

        if asset_type:
            reasons.append("asset_type_filter_applied")

        if language:
            reasons.append("language_filter_applied")

        if framework:
            reasons.append("framework_filter_applied")

        if runtime:
            reasons.append("runtime_filter_applied")

        if platform:
            reasons.append("platform_filter_applied")

        if tags:
            reasons.append("tag_filter_applied")

        if offline_only:
            reasons.append("offline_filter_applied")

        if context is not None:
            reasons.append("catalog_context_applied")

        if returned:
            reasons.append("catalog_entries_found")
        else:
            reasons.append("catalog_entries_not_found")

        return OfflineCatalogResult(
            entries=returned,
            query=query,
            total_count=len(entries),
            returned_count=len(returned),
            context_key=(
                ""
                if context is None
                else context.key()
            ),
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
        )

    def android_entries(
        self,
        *,
        offline_only: bool = True,
    ) -> OfflineCatalogResult:
        return self.search(
            platform="android",
            offline_only=offline_only,
        )

    def by_type(
        self,
        asset_type: str,
    ) -> OfflineCatalogResult:
        return self.search(
            asset_type=asset_type,
        )

    def by_tag(
        self,
        tag: str,
    ) -> OfflineCatalogResult:
        if not tag.strip():
            raise ValueError(
                "tag must not be empty"
            )

        return self.search(
            tags=(tag,),
        )

    def remove(
        self,
        asset_id: str,
    ) -> OfflineCatalogEntry | None:
        return self._entries.pop(
            asset_id,
            None,
        )

    def clear(self) -> None:
        self._entries.clear()

    def count(self) -> int:
        return len(self._entries)

    def to_dict(self) -> dict:
        entries = self.list_entries()

        return {
            "entries": [
                entry.to_dict()
                for entry in entries
            ],
            "count": len(entries),
        }


__all__ = [
    "OfflineCatalogContext",
    "OfflineCatalogEntry",
    "OfflineCatalogResult",
    "CodeLibraryOfflineCatalog",
]
