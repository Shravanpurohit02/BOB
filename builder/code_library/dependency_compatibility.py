from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAsset


@dataclass(frozen=True)
class DependencyCompatibilityContext:
    """Dependency state of the target project."""

    dependencies: tuple[str, ...] = ()
    optional_dependencies: tuple[str, ...] = ()
    blocked_dependencies: tuple[str, ...] = ()
    dependency_versions: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class DependencyCompatibilityResult:
    """Dependency compatibility analysis for one Code Library asset."""

    asset_id: str
    compatible: bool
    score: float
    required_dependencies: tuple[str, ...] = ()
    satisfied_dependencies: tuple[str, ...] = ()
    missing_dependencies: tuple[str, ...] = ()
    optional_matches: tuple[str, ...] = ()
    blocked_dependencies: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "compatible": self.compatible,
            "score": self.score,
            "required_dependencies": list(
                self.required_dependencies
            ),
            "satisfied_dependencies": list(
                self.satisfied_dependencies
            ),
            "missing_dependencies": list(
                self.missing_dependencies
            ),
            "optional_matches": list(
                self.optional_matches
            ),
            "blocked_dependencies": list(
                self.blocked_dependencies
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryDependencyCompatibilityEngine:
    """Analyzes asset dependencies against a project dependency state."""

    MAX_SCORE = 10.0
    COMPATIBILITY_THRESHOLD = 7.0

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def analyze(
        self,
        asset: CodeAsset,
        context: DependencyCompatibilityContext,
    ) -> DependencyCompatibilityResult:
        required = self._normalize(asset.dependencies)
        installed = self._normalize(context.dependencies)
        optional = self._normalize(context.optional_dependencies)
        blocked = self._normalize(context.blocked_dependencies)

        installed_set = set(installed)
        optional_set = set(optional)
        blocked_set = set(blocked)

        satisfied = tuple(
            dependency
            for dependency in required
            if dependency in installed_set
        )

        missing = tuple(
            dependency
            for dependency in required
            if dependency not in installed_set
            and dependency not in optional_set
        )

        optional_matches = tuple(
            dependency
            for dependency in required
            if dependency not in installed_set
            and dependency in optional_set
        )

        blocked_matches = tuple(
            dependency
            for dependency in required
            if dependency in blocked_set
        )

        reasons: list[str] = []

        if satisfied:
            reasons.append("required_dependencies_satisfied")

        if optional_matches:
            reasons.append("optional_dependencies_available")

        if missing:
            reasons.append("required_dependencies_missing")

        if blocked_matches:
            reasons.append("blocked_dependency_detected")

        if not required:
            reasons.append("no_dependencies_required")

        if blocked_matches:
            compatible = False
            score = 0.0
        elif missing:
            compatible = False
            score = self._partial_score(
                required,
                satisfied,
                optional_matches,
            )
        elif required:
            compatible = True
            score = 10.0
        else:
            compatible = True
            score = 10.0

        return DependencyCompatibilityResult(
            asset_id=asset.id,
            compatible=compatible,
            score=round(score, 6),
            required_dependencies=required,
            satisfied_dependencies=satisfied,
            missing_dependencies=missing,
            optional_matches=optional_matches,
            blocked_dependencies=blocked_matches,
            reasons=tuple(reasons),
            metadata=self._metadata(asset, context),
        )

    def analyze_asset(
        self,
        asset_id: str,
        context: DependencyCompatibilityContext,
    ) -> DependencyCompatibilityResult:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        return self.analyze(asset, context)

    def analyze_all(
        self,
        context: DependencyCompatibilityContext,
    ) -> tuple[DependencyCompatibilityResult, ...]:
        results = tuple(
            self.analyze(asset, context)
            for asset in self.engine.list_assets()
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    -item.score,
                    item.asset_id,
                ),
            )
        )

    def compatible_assets(
        self,
        context: DependencyCompatibilityContext,
    ) -> tuple[DependencyCompatibilityResult, ...]:
        return tuple(
            result
            for result in self.analyze_all(context)
            if result.compatible
        )

    @staticmethod
    def _normalize(
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                value.strip().lower()
                for value in values
                if value.strip()
            )
        )

    @staticmethod
    def _partial_score(
        required: tuple[str, ...],
        satisfied: tuple[str, ...],
        optional_matches: tuple[str, ...],
    ) -> float:
        if not required:
            return 10.0

        coverage = (
            len(satisfied) + len(optional_matches)
        ) / len(required)

        return min(
            6.0,
            round(coverage * 6.0, 6),
        )

    @staticmethod
    def _metadata(
        asset: CodeAsset,
        context: DependencyCompatibilityContext,
    ) -> dict[str, Any]:
        return {
            "name": asset.name,
            "version": asset.version,
            "asset_dependencies": list(asset.dependencies),
            "project_dependencies": list(context.dependencies),
            "project_optional_dependencies": list(
                context.optional_dependencies
            ),
            "project_blocked_dependencies": list(
                context.blocked_dependencies
            ),
            "dependency_versions": dict(
                context.dependency_versions
            ),
        }


dependency_compatibility = (
    CodeLibraryDependencyCompatibilityEngine()
)


__all__ = (
    "DependencyCompatibilityContext",
    "DependencyCompatibilityResult",
    "CodeLibraryDependencyCompatibilityEngine",
    "dependency_compatibility",
)
