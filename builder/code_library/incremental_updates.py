from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .resource_index import (
    CodeLibraryResourceIndex,
    ResourceIndexEntry,
)


@dataclass(frozen=True)
class IncrementalUpdate:
    operation: str
    asset_id: str
    terms: tuple[str, ...] = ()
    metadata: dict | None = None
    value: Any = None
    version: int = 1

    def __post_init__(self) -> None:
        operation = self.operation.strip().lower()

        if operation not in {
            "add",
            "update",
            "remove",
        }:
            raise ValueError(
                "operation must be add, update, or remove"
            )

        if not self.asset_id.strip():
            raise ValueError(
                "asset_id must not be empty"
            )

        if self.version < 1:
            raise ValueError(
                "version must be positive"
            )

        object.__setattr__(
            self,
            "operation",
            operation,
        )

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "asset_id": self.asset_id,
            "terms": list(self.terms),
            "metadata": dict(self.metadata or {}),
            "value": self.value,
            "version": self.version,
        }


@dataclass(frozen=True)
class IncrementalUpdateResult:
    applied: tuple[IncrementalUpdate, ...]
    rejected: tuple[IncrementalUpdate, ...]
    added_asset_ids: tuple[str, ...]
    updated_asset_ids: tuple[str, ...]
    removed_asset_ids: tuple[str, ...]
    unchanged_asset_ids: tuple[str, ...]
    success: bool
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "applied": [
                item.to_dict()
                for item in self.applied
            ],
            "rejected": [
                item.to_dict()
                for item in self.rejected
            ],
            "added_asset_ids": list(
                self.added_asset_ids
            ),
            "updated_asset_ids": list(
                self.updated_asset_ids
            ),
            "removed_asset_ids": list(
                self.removed_asset_ids
            ),
            "unchanged_asset_ids": list(
                self.unchanged_asset_ids
            ),
            "success": self.success,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryIncrementalUpdater:
    """
    Applies Code Library changes directly to a resource index.

    Only affected assets are touched. No full index rebuild is required.
    """

    def __init__(
        self,
        index: CodeLibraryResourceIndex,
    ) -> None:
        if not isinstance(
            index,
            CodeLibraryResourceIndex,
        ):
            raise TypeError(
                "index must be CodeLibraryResourceIndex"
            )

        self.index = index

    @staticmethod
    def _normalize_terms(
        terms: Iterable[str],
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                dict.fromkeys(
                    term.strip().lower()
                    for term in terms
                    if isinstance(term, str)
                    and term.strip()
                )
            )
        )

    def apply(
        self,
        update: IncrementalUpdate,
    ) -> IncrementalUpdateResult:
        if not isinstance(
            update,
            IncrementalUpdate,
        ):
            raise TypeError(
                "update must be IncrementalUpdate"
            )

        before = self.index.get(
            update.asset_id
        )

        applied: tuple[
            IncrementalUpdate, ...
        ] = ()

        added: tuple[str, ...] = ()
        updated: tuple[str, ...] = ()
        removed: tuple[str, ...] = ()
        unchanged: tuple[str, ...] = ()
        rejected: tuple[
            IncrementalUpdate, ...
        ] = ()

        if update.operation == "add":
            if before is not None:
                rejected = (update,)
            else:
                self.index.add(
                    update.asset_id,
                    update.terms,
                    metadata=update.metadata,
                )
                applied = (update,)
                added = (update.asset_id,)

        elif update.operation == "update":
            if before is None:
                rejected = (update,)
            else:
                terms = self._normalize_terms(
                    update.terms
                )
                current_terms = before.terms
                current_metadata = before.metadata

                if (
                    terms == current_terms
                    and dict(
                        update.metadata or {}
                    )
                    == current_metadata
                ):
                    applied = (update,)
                    unchanged = (
                        update.asset_id,
                    )
                else:
                    self.index.update(
                        update.asset_id,
                        terms,
                        metadata=update.metadata,
                    )
                    applied = (update,)
                    updated = (
                        update.asset_id,
                    )

        elif update.operation == "remove":
            if before is None:
                rejected = (update,)
            else:
                self.index.remove(
                    update.asset_id
                )
                applied = (update,)
                removed = (
                    update.asset_id,
                )

        success = not rejected

        reasons: list[str] = []

        if added:
            reasons.append("asset_added")

        if updated:
            reasons.append("asset_updated")

        if removed:
            reasons.append("asset_removed")

        if unchanged:
            reasons.append("asset_unchanged")

        if rejected:
            reasons.append("update_rejected")

        if success:
            reasons.append("incremental_update_applied")
        else:
            reasons.append("incremental_update_blocked")

        return IncrementalUpdateResult(
            applied=applied,
            rejected=rejected,
            added_asset_ids=added,
            updated_asset_ids=updated,
            removed_asset_ids=removed,
            unchanged_asset_ids=unchanged,
            success=success,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "requested_count": 1,
                "applied_count": len(applied),
                "rejected_count": len(rejected),
                "index_asset_count": self.index.count(),
                "index_term_count": self.index.term_count(),
            },
        )

    def apply_many(
        self,
        updates: Iterable[IncrementalUpdate],
    ) -> IncrementalUpdateResult:
        normalized = tuple(updates)

        applied: list[IncrementalUpdate] = []
        rejected: list[IncrementalUpdate] = []
        added: list[str] = []
        updated: list[str] = []
        removed: list[str] = []
        unchanged: list[str] = []

        for update in normalized:
            result = self.apply(update)

            applied.extend(result.applied)
            rejected.extend(result.rejected)
            added.extend(result.added_asset_ids)
            updated.extend(result.updated_asset_ids)
            removed.extend(result.removed_asset_ids)
            unchanged.extend(
                result.unchanged_asset_ids
            )

        success = not rejected

        reasons: list[str] = []

        if added:
            reasons.append("assets_added")

        if updated:
            reasons.append("assets_updated")

        if removed:
            reasons.append("assets_removed")

        if unchanged:
            reasons.append("assets_unchanged")

        if rejected:
            reasons.append("updates_rejected")

        if success:
            reasons.append(
                "incremental_batch_applied"
            )
        else:
            reasons.append(
                "incremental_batch_partial"
            )

        return IncrementalUpdateResult(
            applied=tuple(applied),
            rejected=tuple(rejected),
            added_asset_ids=tuple(
                dict.fromkeys(added)
            ),
            updated_asset_ids=tuple(
                dict.fromkeys(updated)
            ),
            removed_asset_ids=tuple(
                dict.fromkeys(removed)
            ),
            unchanged_asset_ids=tuple(
                dict.fromkeys(unchanged)
            ),
            success=success,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "requested_count": len(normalized),
                "applied_count": len(applied),
                "rejected_count": len(rejected),
                "index_asset_count": self.index.count(),
                "index_term_count": self.index.term_count(),
            },
        )

    def add(
        self,
        asset_id: str,
        terms: Iterable[str],
        *,
        metadata: dict | None = None,
        version: int = 1,
    ) -> IncrementalUpdateResult:
        return self.apply(
            IncrementalUpdate(
                operation="add",
                asset_id=asset_id,
                terms=tuple(terms),
                metadata=metadata,
                version=version,
            )
        )

    def update(
        self,
        asset_id: str,
        terms: Iterable[str],
        *,
        metadata: dict | None = None,
        version: int = 1,
    ) -> IncrementalUpdateResult:
        return self.apply(
            IncrementalUpdate(
                operation="update",
                asset_id=asset_id,
                terms=tuple(terms),
                metadata=metadata,
                version=version,
            )
        )

    def remove(
        self,
        asset_id: str,
        *,
        version: int = 1,
    ) -> IncrementalUpdateResult:
        return self.apply(
            IncrementalUpdate(
                operation="remove",
                asset_id=asset_id,
                version=version,
            )
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.index.contains(asset_id)

    def snapshot(self) -> dict:
        return self.index.export_payload()


__all__ = [
    "IncrementalUpdate",
    "IncrementalUpdateResult",
    "CodeLibraryIncrementalUpdater",
]
