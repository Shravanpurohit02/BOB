from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .compatibility import (
    AssetCompatibilityContext,
    AssetCompatibilityScore,
    CodeLibraryCompatibilityEngine,
)
from .conflict_analysis import (
    AssetConflictContext,
    AssetConflictResult,
    CodeLibraryConflictAnalysisEngine,
)
from .dependency_compatibility import (
    DependencyCompatibilityContext,
    DependencyCompatibilityResult,
    CodeLibraryDependencyCompatibilityEngine,
)
from .engine import CodeLibraryEngine


@dataclass(frozen=True)
class CompatibilityDecision:
    """Final compatibility decision for a Code Library asset."""

    asset_id: str
    decision: str
    compatible: bool
    score: float
    reasons: tuple[str, ...] = ()
    compatibility: AssetCompatibilityScore | None = None
    dependency: DependencyCompatibilityResult | None = None
    conflict: AssetConflictResult | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "decision": self.decision,
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "compatibility": (
                self.compatibility.to_dict()
                if self.compatibility is not None
                else None
            ),
            "dependency": (
                self.dependency.to_dict()
                if self.dependency is not None
                else None
            ),
            "conflict": (
                self.conflict.to_dict()
                if self.conflict is not None
                else None
            ),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryCompatibilityDecisionEngine:
    """Combines compatibility, dependency, and conflict analysis."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

        self.compatibility = CodeLibraryCompatibilityEngine(
            self.engine
        )
        self.dependencies = (
            CodeLibraryDependencyCompatibilityEngine(
                self.engine
            )
        )
        self.conflicts = CodeLibraryConflictAnalysisEngine(
            self.engine
        )

    def decide(
        self,
        asset_id: str,
        *,
        compatibility_context: AssetCompatibilityContext | None = None,
        dependency_context: DependencyCompatibilityContext | None = None,
        conflict_context: AssetConflictContext | None = None,
    ) -> CompatibilityDecision:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        compatibility_context = (
            compatibility_context
            or AssetCompatibilityContext()
        )
        dependency_context = (
            dependency_context
            or DependencyCompatibilityContext()
        )
        conflict_context = (
            conflict_context
            or AssetConflictContext()
        )

        compatibility = self.compatibility.score(
            asset,
            compatibility_context,
        )

        dependency = self.dependencies.analyze(
            asset,
            dependency_context,
        )

        conflict = self.conflicts.analyze(
            asset,
            conflict_context,
        )

        reasons: list[str] = []

        if compatibility.compatible:
            reasons.append("compatibility_pass")

        if dependency.compatible:
            reasons.append("dependency_pass")

        if conflict.conflicted:
            reasons.append("conflict_detected")

        if not compatibility.compatible:
            reasons.extend(
                f"compatibility:{reason}"
                for reason in compatibility.reasons
            )

        if not dependency.compatible:
            reasons.extend(
                f"dependency:{reason}"
                for reason in dependency.reasons
            )

        if conflict.conflicted:
            reasons.extend(
                f"conflict:{reason}"
                for reason in conflict.reasons
            )

        if asset.lifecycle == "deprecated":
            decision = "reject"
            compatible = False
        elif conflict.severity == "critical":
            decision = "reject"
            compatible = False
        elif not compatibility.compatible:
            decision = "reject"
            compatible = False
        elif not dependency.compatible:
            decision = "review"
            compatible = False
        elif conflict.conflicted:
            decision = "review"
            compatible = False
        else:
            decision = "accept"
            compatible = True

        score = self._decision_score(
            compatibility,
            dependency,
            conflict,
            decision,
        )

        return CompatibilityDecision(
            asset_id=asset_id,
            decision=decision,
            compatible=compatible,
            score=score,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            compatibility=compatibility,
            dependency=dependency,
            conflict=conflict,
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

    def decide_many(
        self,
        asset_ids: tuple[str, ...],
        *,
        compatibility_context: AssetCompatibilityContext | None = None,
        dependency_context: DependencyCompatibilityContext | None = None,
        conflict_context: AssetConflictContext | None = None,
    ) -> tuple[CompatibilityDecision, ...]:
        results = tuple(
            self.decide(
                asset_id,
                compatibility_context=compatibility_context,
                dependency_context=dependency_context,
                conflict_context=conflict_context,
            )
            for asset_id in dict.fromkeys(asset_ids)
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    self._decision_rank(item.decision),
                    -item.score,
                    item.asset_id,
                ),
            )
        )

    def accepted(
        self,
        asset_ids: tuple[str, ...],
        *,
        compatibility_context: AssetCompatibilityContext | None = None,
        dependency_context: DependencyCompatibilityContext | None = None,
        conflict_context: AssetConflictContext | None = None,
    ) -> tuple[CompatibilityDecision, ...]:
        return tuple(
            result
            for result in self.decide_many(
                asset_ids,
                compatibility_context=compatibility_context,
                dependency_context=dependency_context,
                conflict_context=conflict_context,
            )
            if result.decision == "accept"
        )

    @staticmethod
    def _decision_score(
        compatibility: AssetCompatibilityScore,
        dependency: DependencyCompatibilityResult,
        conflict: AssetConflictResult,
        decision: str,
    ) -> float:
        if decision == "reject":
            return 0.0

        score = (
            compatibility.score * 0.6
            + dependency.score * 0.4
        )

        if conflict.conflicted:
            score *= 0.5

        return round(
            max(0.0, min(10.0, score)),
            6,
        )

    @staticmethod
    def _decision_rank(decision: str) -> int:
        return {
            "accept": 0,
            "review": 1,
            "reject": 2,
        }.get(decision, 3)


compatibility_decision = (
    CodeLibraryCompatibilityDecisionEngine()
)


__all__ = (
    "CompatibilityDecision",
    "CodeLibraryCompatibilityDecisionEngine",
    "compatibility_decision",
)
