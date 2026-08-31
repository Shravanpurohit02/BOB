from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetLifecycle, CodeAssetRelationship


@dataclass(frozen=True)
class CodeAssetSupersessionDecision:
    """Deterministic CL-10.8 supersession decision."""

    asset_id: str
    superseding_asset_id: str
    eligible: bool
    reason: str
    source: str = "code-library"

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "superseding_asset_id": self.superseding_asset_id,
            "eligible": self.eligible,
            "reason": self.reason,
            "source": self.source,
        }


class CodeLibrarySupersessionManager:
    """CL-10.8 manager for explicit asset supersession.

    Supersession records the relationship between an older asset and the
    asset that replaces it. It does not automatically delete the old asset
    or alter unrelated lifecycle state.
    """

    RELATION = "superseded_by"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def evaluate(
        self,
        asset_id: str,
        superseding_asset_id: str,
        *,
        reason: str = "",
        source: str = "code-library",
    ) -> CodeAssetSupersessionDecision:
        asset = self._require(asset_id)
        superseding = self._require(superseding_asset_id)

        if asset.id == superseding.id:
            raise ValueError(
                "An asset cannot supersede itself"
            )

        if asset.lifecycle == CodeAssetLifecycle.DEPRECATED.value:
            return CodeAssetSupersessionDecision(
                asset_id=asset.id,
                superseding_asset_id=superseding.id,
                eligible=False,
                reason="asset_already_deprecated",
                source=source,
            )

        if superseding.lifecycle == CodeAssetLifecycle.DEPRECATED.value:
            return CodeAssetSupersessionDecision(
                asset_id=asset.id,
                superseding_asset_id=superseding.id,
                eligible=False,
                reason="superseding_asset_is_deprecated",
                source=source,
            )

        normalized_reason = str(reason).strip()

        return CodeAssetSupersessionDecision(
            asset_id=asset.id,
            superseding_asset_id=superseding.id,
            eligible=True,
            reason=(
                normalized_reason
                or "superseding_asset_selected"
            ),
            source=source,
        )

    def supersede(
        self,
        asset_id: str,
        superseding_asset_id: str,
        *,
        reason: str = "",
        source: str = "code-library",
    ) -> CodeAssetSupersessionDecision:
        decision = self.evaluate(
            asset_id,
            superseding_asset_id,
            reason=reason,
            source=source,
        )

        if not decision.eligible:
            return decision

        asset = self._require(asset_id)

        existing = [
            relationship
            for relationship in asset.relationships
            if (
                relationship.relation == self.RELATION
                and relationship.target_id
                == superseding_asset_id
            )
        ]

        if not existing:
            asset.relationships.append(
                CodeAssetRelationship(
                    source_id=asset_id,
                    target_id=superseding_asset_id,
                    relation=self.RELATION,
                    metadata={
                        "reason": decision.reason,
                        "source": decision.source,
                    },
                )
            )

        asset.metadata = dict(asset.metadata)
        asset.metadata["supersession"] = {
            "superseded_by": superseding_asset_id,
            "reason": decision.reason,
            "source": decision.source,
        }

        self.engine.store.save(asset)

        return decision

    def superseded_by(
        self,
        asset_id: str,
    ) -> str | None:
        asset = self._require(asset_id)

        for relationship in asset.relationships:
            if relationship.relation == self.RELATION:
                return relationship.target_id

        return None

    def is_superseded(
        self,
        asset_id: str,
    ) -> bool:
        return self.superseded_by(asset_id) is not None

    def get_superseded_assets(
        self,
        superseding_asset_id: str,
    ) -> tuple[CodeAsset, ...]:
        self._require(superseding_asset_id)

        assets: list[CodeAsset] = []

        for asset in self.engine.list_assets():
            if self.superseded_by(asset.id) == superseding_asset_id:
                assets.append(asset)

        return tuple(
            sorted(
                assets,
                key=lambda item: item.id,
            )
        )

    def _require(
        self,
        asset_id: str,
    ) -> CodeAsset:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        return asset


supersession_manager = CodeLibrarySupersessionManager()


__all__ = (
    "CodeAssetSupersessionDecision",
    "CodeLibrarySupersessionManager",
    "supersession_manager",
)
