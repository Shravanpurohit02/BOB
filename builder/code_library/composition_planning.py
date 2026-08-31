from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .compatibility_decision import (
    CompatibilityDecision,
    CodeLibraryCompatibilityDecisionEngine,
)
from .compatibility import AssetCompatibilityContext
from .conflict_analysis import AssetConflictContext
from .dependency_compatibility import DependencyCompatibilityContext
from .engine import CodeLibraryEngine


@dataclass(frozen=True)
class CompositionPlanContext:
    """Project requirements used to create an asset composition plan."""

    asset_ids: tuple[str, ...] = ()
    language: str = ""
    framework: str = ""
    runtime: str = ""
    asset_type: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompositionPlanItem:
    """One selected asset in a composition plan."""

    asset_id: str
    decision: str
    score: float
    order: int
    dependencies: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "decision": self.decision,
            "score": self.score,
            "order": self.order,
            "dependencies": list(self.dependencies),
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class CompositionPlan:
    """Deterministic plan for composing compatible Code Library assets."""

    items: tuple[CompositionPlanItem, ...]
    selected_asset_ids: tuple[str, ...]
    rejected_asset_ids: tuple[str, ...]
    review_asset_ids: tuple[str, ...]
    dependency_order: tuple[str, ...]
    compatible: bool
    score: float
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "selected_asset_ids": list(
                self.selected_asset_ids
            ),
            "rejected_asset_ids": list(
                self.rejected_asset_ids
            ),
            "review_asset_ids": list(
                self.review_asset_ids
            ),
            "dependency_order": list(
                self.dependency_order
            ),
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryCompositionPlanningEngine:
    """Builds deterministic asset composition plans."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.decisions = (
            CodeLibraryCompatibilityDecisionEngine(
                self.engine
            )
        )

    def plan(
        self,
        asset_ids: tuple[str, ...],
        context: CompositionPlanContext | None = None,
    ) -> CompositionPlan:
        context = context or CompositionPlanContext()

        unique_ids = tuple(
            dict.fromkeys(asset_ids)
        )

        for asset_id in unique_ids:
            if self.engine.get(asset_id) is None:
                raise ValueError(
                    f"Code Library asset not found: {asset_id}"
                )

        compatibility_context = AssetCompatibilityContext(
            language=context.language,
            framework=context.framework,
            runtime=context.runtime,
            asset_type=context.asset_type,
            capabilities=context.capabilities,
            dependencies=context.dependencies,
        )

        # Dependencies supplied by the project context are external
        # dependencies. Dependencies between selected Code Library
        # assets must also be considered satisfied when the referenced
        # asset is part of this composition.
        selected_dependency_names: list[str] = list(
            context.dependencies
        )

        selected_assets = {
            asset_id: self.engine.get(asset_id)
            for asset_id in unique_ids
        }

        for selected_asset in selected_assets.values():
            if selected_asset is None:
                continue

            selected_dependency_names.append(
                selected_asset.id
            )
            selected_dependency_names.append(
                selected_asset.name
            )

        dependency_context = DependencyCompatibilityContext(
            dependencies=tuple(
                dict.fromkeys(
                    value.strip()
                    for value in selected_dependency_names
                    if value.strip()
                )
            ),
        )

        conflict_context = AssetConflictContext(
            existing_asset_ids=context.asset_ids,
            existing_capabilities=context.capabilities,
            existing_dependencies=context.dependencies,
            language=context.language,
            framework=context.framework,
            runtime=context.runtime,
            asset_type=context.asset_type,
        )

        decisions = self.decisions.decide_many(
            unique_ids,
            compatibility_context=compatibility_context,
            dependency_context=dependency_context,
            conflict_context=conflict_context,
        )

        decision_map = {
            decision.asset_id: decision
            for decision in decisions
        }

        selected = tuple(
            decision.asset_id
            for decision in decisions
            if decision.decision == "accept"
            and decision.asset_id not in context.asset_ids
        )

        rejected = tuple(
            decision.asset_id
            for decision in decisions
            if decision.decision == "reject"
        )

        review = tuple(
            decision.asset_id
            for decision in decisions
            if decision.decision == "review"
        )

        dependency_order = self._dependency_order(
            selected,
            decision_map,
        )

        items: list[CompositionPlanItem] = []

        for index, asset_id in enumerate(
            dependency_order,
            start=1,
        ):
            decision = decision_map[asset_id]
            asset = self.engine.get(asset_id)

            items.append(
                CompositionPlanItem(
                    asset_id=asset_id,
                    decision=decision.decision,
                    score=decision.score,
                    order=index,
                    dependencies=tuple(
                        dependency
                        for dependency in (
                            asset.dependencies
                            if asset is not None
                            else ()
                        )
                        if dependency in selected
                    ),
                    reasons=decision.reasons,
                )
            )

        reasons: list[str] = []

        if selected:
            reasons.append("compatible_assets_selected")

        if rejected:
            reasons.append("incompatible_assets_rejected")

        if review:
            reasons.append("assets_require_review")

        if dependency_order:
            reasons.append("dependency_order_resolved")

        if not selected:
            reasons.append("no_assets_selected")

        compatible = bool(selected) and not rejected and not review

        if compatible:
            reasons.append("composition_plan_compatible")

        score = self._plan_score(
            decisions,
            selected,
        )

        return CompositionPlan(
            items=tuple(items),
            selected_asset_ids=selected,
            rejected_asset_ids=rejected,
            review_asset_ids=review,
            dependency_order=dependency_order,
            compatible=compatible,
            score=score,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "requested_asset_count": len(unique_ids),
                "selected_asset_count": len(selected),
                "rejected_asset_count": len(rejected),
                "review_asset_count": len(review),
            },
        )

    def plan_all(
        self,
        context: CompositionPlanContext | None = None,
    ) -> CompositionPlan:
        context = context or CompositionPlanContext()

        return self.plan(
            tuple(
                asset.id
                for asset in self.engine.list_assets()
            ),
            context,
        )

    @staticmethod
    def _dependency_order(
        selected: tuple[str, ...],
        decisions: dict[str, CompatibilityDecision],
    ) -> tuple[str, ...]:
        selected_set = set(selected)
        dependencies: dict[str, set[str]] = {
            asset_id: set()
            for asset_id in selected
        }

        for asset_id in selected:
            decision = decisions[asset_id]

            dependency_result = decision.dependency

            if dependency_result is None:
                continue

            for dependency in (
                dependency_result.satisfied_dependencies
            ):
                if dependency in selected_set:
                    dependencies[asset_id].add(
                        dependency
                    )

        ordered: list[str] = []
        remaining = set(selected)

        while remaining:
            ready = sorted(
                asset_id
                for asset_id in remaining
                if not (
                    dependencies[asset_id]
                    & remaining
                )
            )

            if not ready:
                ready = [min(remaining)]

            for asset_id in ready:
                ordered.append(asset_id)
                remaining.remove(asset_id)

        return tuple(ordered)

    @staticmethod
    def _plan_score(
        decisions: tuple[CompatibilityDecision, ...],
        selected: tuple[str, ...],
    ) -> float:
        if not selected:
            return 0.0

        selected_set = set(selected)

        scores = [
            decision.score
            for decision in decisions
            if decision.asset_id in selected_set
        ]

        if not scores:
            return 0.0

        return round(
            sum(scores) / len(scores),
            6,
        )


composition_planning = (
    CodeLibraryCompositionPlanningEngine()
)


__all__ = (
    "CompositionPlanContext",
    "CompositionPlanItem",
    "CompositionPlan",
    "CodeLibraryCompositionPlanningEngine",
    "composition_planning",
)
