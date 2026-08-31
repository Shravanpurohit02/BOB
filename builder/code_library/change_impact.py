from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dependency_impact import (
    CodeLibraryDependencyImpactEngine,
    DependencyImpactResult,
)
from .dependency_graph import DependencyGraphContext
from .engine import CodeLibraryEngine


@dataclass(frozen=True)
class AssetChangeContext:
    """Description of a proposed change to a Code Library asset."""

    change_type: str = "modify"
    changed_fields: tuple[str, ...] = ()
    breaking: bool = False
    new_dependencies: tuple[str, ...] = ()
    removed_dependencies: tuple[str, ...] = ()
    new_capabilities: tuple[str, ...] = ()
    removed_capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssetChangeImpactResult:
    """Predicted impact of changing one Code Library asset."""

    asset_id: str
    change_type: str
    breaking: bool
    risk: str
    direct_dependents: tuple[str, ...] = ()
    transitive_dependents: tuple[str, ...] = ()
    affected_assets: tuple[str, ...] = ()
    affected_count: int = 0
    dependency_changes: tuple[str, ...] = ()
    capability_changes: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "change_type": self.change_type,
            "breaking": self.breaking,
            "risk": self.risk,
            "direct_dependents": list(self.direct_dependents),
            "transitive_dependents": list(
                self.transitive_dependents
            ),
            "affected_assets": list(self.affected_assets),
            "affected_count": self.affected_count,
            "dependency_changes": list(
                self.dependency_changes
            ),
            "capability_changes": list(
                self.capability_changes
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryChangeImpactEngine:
    """Predicts downstream impact from proposed asset changes."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.impact = CodeLibraryDependencyImpactEngine(
            self.engine
        )

    def predict(
        self,
        asset_id: str,
        change: AssetChangeContext | None = None,
        context: DependencyGraphContext | None = None,
    ) -> AssetChangeImpactResult:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        change = change or AssetChangeContext()

        impact: DependencyImpactResult = self.impact.analyze(
            asset_id,
            context,
        )

        dependency_changes = tuple(
            dict.fromkeys(
                [
                    *(
                        f"added:{value.strip().lower()}"
                        for value in change.new_dependencies
                        if value.strip()
                    ),
                    *(
                        f"removed:{value.strip().lower()}"
                        for value in change.removed_dependencies
                        if value.strip()
                    ),
                ]
            )
        )

        capability_changes = tuple(
            dict.fromkeys(
                [
                    *(
                        f"added:{value.strip().lower()}"
                        for value in change.new_capabilities
                        if value.strip()
                    ),
                    *(
                        f"removed:{value.strip().lower()}"
                        for value in change.removed_capabilities
                        if value.strip()
                    ),
                ]
            )
        )

        reasons: list[str] = []

        if impact.direct_dependents:
            reasons.append("direct_dependents_affected")

        if impact.transitive_dependents:
            reasons.append("transitive_dependents_affected")

        if change.breaking:
            reasons.append("breaking_change")

        if dependency_changes:
            reasons.append("dependency_surface_changed")

        if capability_changes:
            reasons.append("capability_surface_changed")

        if change.change_type == "remove":
            reasons.append("asset_removal")

        if change.change_type == "deprecate":
            reasons.append("asset_deprecation")

        if impact.critical:
            reasons.append("critical_dependency_impact")

        risk = self._risk(
            change=change,
            impact=impact,
            dependency_changes=dependency_changes,
            capability_changes=capability_changes,
        )

        return AssetChangeImpactResult(
            asset_id=asset_id,
            change_type=change.change_type,
            breaking=change.breaking,
            risk=risk,
            direct_dependents=impact.direct_dependents,
            transitive_dependents=impact.transitive_dependents,
            affected_assets=impact.affected_assets,
            affected_count=impact.affected_count,
            dependency_changes=dependency_changes,
            capability_changes=capability_changes,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "name": asset.name,
                "asset_type": asset.asset_type,
                "language": asset.language,
                "framework": asset.framework,
                "runtime": asset.runtime,
                "version": asset.version,
                "lifecycle": asset.lifecycle,
            },
        )

    def predict_many(
        self,
        changes: tuple[
            tuple[str, AssetChangeContext],
            ...,
        ],
        context: DependencyGraphContext | None = None,
    ) -> tuple[AssetChangeImpactResult, ...]:
        results = tuple(
            self.predict(
                asset_id,
                change,
                context,
            )
            for asset_id, change in changes
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    -self._risk_rank(item.risk),
                    -item.affected_count,
                    item.asset_id,
                ),
            )
        )

    def highest_risk(
        self,
        context: DependencyGraphContext | None = None,
    ) -> tuple[AssetChangeImpactResult, ...]:
        results = tuple(
            self.predict(
                asset.id,
                AssetChangeContext(),
                context,
            )
            for asset in self.engine.list_assets()
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    -self._risk_rank(item.risk),
                    -item.affected_count,
                    item.asset_id,
                ),
            )
        )

    @staticmethod
    def _risk(
        *,
        change: AssetChangeContext,
        impact: DependencyImpactResult,
        dependency_changes: tuple[str, ...],
        capability_changes: tuple[str, ...],
    ) -> str:
        if change.change_type == "remove":
            return "critical"

        if change.breaking and impact.affected_count:
            return "critical"

        if impact.critical:
            return "critical"

        if change.breaking:
            return "high"

        if impact.affected_count >= 2:
            return "high"

        if (
            dependency_changes
            or capability_changes
            or impact.affected_count == 1
        ):
            return "medium"

        return "low"

    @staticmethod
    def _risk_rank(risk: str) -> int:
        return {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }.get(risk, 0)


change_impact = CodeLibraryChangeImpactEngine()


__all__ = (
    "AssetChangeContext",
    "AssetChangeImpactResult",
    "CodeLibraryChangeImpactEngine",
    "change_impact",
)
