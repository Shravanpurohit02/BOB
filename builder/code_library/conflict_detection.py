from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset


@dataclass(frozen=True)
class CodeAssetConflict:
    """A detected incompatibility between two Code Library assets."""

    asset_id: str
    conflicting_asset_id: str
    conflict_type: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "conflicting_asset_id": self.conflicting_asset_id,
            "conflict_type": self.conflict_type,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CodeAssetConflictReport:
    """Deterministic conflict projection for one asset."""

    asset_id: str
    conflicts: tuple[CodeAssetConflict, ...]

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "has_conflicts": self.has_conflicts,
            "conflict_count": self.conflict_count,
            "conflicts": [
                conflict.to_dict()
                for conflict in self.conflicts
            ],
        }


class CodeLibraryConflictDetector:
    """CL-10.7 deterministic Code Library conflict detector.

    Conflict detection is analytical only. It does not alter assets,
    lifecycle state, relationships, or versions.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def detect(
        self,
        asset_id: str,
        candidates: Iterable[CodeAsset] | None = None,
    ) -> CodeAssetConflictReport:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        pool = (
            list(candidates)
            if candidates is not None
            else self.engine.list_assets()
        )

        conflicts: list[CodeAssetConflict] = []

        for candidate in pool:
            if candidate.id == asset.id:
                continue

            conflict = self._compare(asset, candidate)

            if conflict is not None:
                conflicts.append(conflict)

        conflicts.sort(
            key=lambda item: (
                item.conflict_type,
                item.conflicting_asset_id,
            )
        )

        return CodeAssetConflictReport(
            asset_id=asset.id,
            conflicts=tuple(conflicts),
        )

    def detect_pair(
        self,
        asset_id: str,
        other_asset_id: str,
    ) -> CodeAssetConflict | None:
        asset = self.engine.get(asset_id)
        other = self.engine.get(other_asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        if other is None:
            raise KeyError(
                f"Code Library asset not found: {other_asset_id}"
            )

        return self._compare(asset, other)

    @staticmethod
    def _compare(
        asset: CodeAsset,
        other: CodeAsset,
    ) -> CodeAssetConflict | None:
        # Same canonical identity with different content/version.
        if asset.name.strip().lower() == other.name.strip().lower():
            if asset.fingerprint != other.fingerprint:
                return CodeAssetConflict(
                    asset_id=asset.id,
                    conflicting_asset_id=other.id,
                    conflict_type="duplicate_identity",
                    reason=(
                        "Assets have the same canonical name "
                        "but different fingerprints."
                    ),
                )

        # Same runtime target with incompatible framework declarations.
        if (
            asset.language
            and other.language
            and asset.language.lower() == other.language.lower()
            and asset.framework
            and other.framework
            and asset.framework.lower() != other.framework.lower()
        ):
            return CodeAssetConflict(
                asset_id=asset.id,
                conflicting_asset_id=other.id,
                conflict_type="framework_conflict",
                reason=(
                    "Assets target the same language but declare "
                    "different frameworks."
                ),
            )

        # Explicit relationship conflicts.
        for relationship in asset.relationships:
            if (
                relationship.target_id == other.id
                and relationship.relation.lower()
                in {
                    "conflicts",
                    "incompatible",
                    "mutually_exclusive",
                }
            ):
                return CodeAssetConflict(
                    asset_id=asset.id,
                    conflicting_asset_id=other.id,
                    conflict_type="declared_conflict",
                    reason=(
                        "Asset declares an incompatible relationship "
                        "with the candidate."
                    ),
                )

        for relationship in other.relationships:
            if (
                relationship.target_id == asset.id
                and relationship.relation.lower()
                in {
                    "conflicts",
                    "incompatible",
                    "mutually_exclusive",
                }
            ):
                return CodeAssetConflict(
                    asset_id=asset.id,
                    conflicting_asset_id=other.id,
                    conflict_type="declared_conflict",
                    reason=(
                        "Candidate declares an incompatible relationship "
                        "with the asset."
                    ),
                )

        return None


conflict_detector = CodeLibraryConflictDetector()


__all__ = (
    "CodeAssetConflict",
    "CodeAssetConflictReport",
    "CodeLibraryConflictDetector",
    "conflict_detector",
)
