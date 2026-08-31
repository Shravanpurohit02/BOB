from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAsset


@dataclass(frozen=True)
class CompositionContext:
    """Existing assets and project state used for composition analysis."""

    asset_ids: tuple[str, ...] = ()
    language: str = ""
    framework: str = ""
    runtime: str = ""
    asset_type: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompositionCompatibilityResult:
    """Compatibility result for composing one asset into a project."""

    asset_id: str
    compatible: bool
    score: float
    reasons: tuple[str, ...] = ()
    missing_dependencies: tuple[str, ...] = ()
    conflicting_assets: tuple[str, ...] = ()
    complementary_assets: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "missing_dependencies": list(self.missing_dependencies),
            "conflicting_assets": list(self.conflicting_assets),
            "complementary_assets": list(
                self.complementary_assets
            ),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryCompositionCompatibilityEngine:
    """Analyzes whether Code Library assets compose cleanly."""

    MAX_SCORE = 10.0
    COMPATIBILITY_THRESHOLD = 6.0

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def analyze(
        self,
        asset: CodeAsset,
        context: CompositionContext,
    ) -> CompositionCompatibilityResult:
        reasons: list[str] = []
        missing_dependencies: list[str] = []
        conflicting_assets: list[str] = []
        complementary_assets: list[str] = []

        score = 0.0

        existing_ids = set(context.asset_ids)

        if asset.id in existing_ids:
            conflicting_assets.append(asset.id)
            reasons.append("asset_already_present")

        if asset.lifecycle == "deprecated":
            reasons.append("deprecated_asset")

        if context.language:
            if asset.language.lower() == context.language.lower():
                score += 2.0
                reasons.append("language_match")
            else:
                reasons.append("language_mismatch")

        if context.framework:
            if asset.framework.lower() == context.framework.lower():
                score += 2.0
                reasons.append("framework_match")
            else:
                reasons.append("framework_mismatch")

        if context.runtime:
            if asset.runtime.lower() == context.runtime.lower():
                score += 1.0
                reasons.append("runtime_match")
            else:
                reasons.append("runtime_mismatch")

        if context.asset_type:
            if asset.asset_type == context.asset_type:
                score += 1.0
                reasons.append("asset_type_match")

        existing_capabilities = {
            value.strip().lower()
            for value in context.capabilities
            if value.strip()
        }
        asset_capabilities = {
            value.strip().lower()
            for value in asset.capabilities
            if value.strip()
        }

        capability_overlap = (
            existing_capabilities & asset_capabilities
        )

        if capability_overlap:
            score += min(
                1.5,
                0.75 * len(capability_overlap),
            )
            reasons.append("capability_overlap")

        existing_dependencies = {
            value.strip().lower()
            for value in context.dependencies
            if value.strip()
        }
        asset_dependencies = {
            value.strip().lower()
            for value in asset.dependencies
            if value.strip()
        }

        missing_dependencies.extend(
            sorted(
                dependency
                for dependency in asset_dependencies
                if dependency not in existing_dependencies
            )
        )

        if not missing_dependencies:
            score += 1.5
            reasons.append("dependencies_available")
        else:
            reasons.append("dependencies_missing")

        for existing_id in context.asset_ids:
            existing = self.engine.get(existing_id)

            if existing is None or existing.id == asset.id:
                continue

            existing_capabilities = {
                value.strip().lower()
                for value in existing.capabilities
                if value.strip()
            }

            existing_dependencies = {
                value.strip().lower()
                for value in existing.dependencies
                if value.strip()
            }

            if asset_capabilities & existing_capabilities:
                complementary_assets.append(existing.id)

            if asset_dependencies & existing_dependencies:
                complementary_assets.append(existing.id)

            if (
                asset.framework
                and existing.framework
                and asset.framework.lower()
                == existing.framework.lower()
                and asset.asset_type == existing.asset_type
                and asset.name.lower() == existing.name.lower()
            ):
                conflicting_assets.append(existing.id)

        complementary_assets = list(
            dict.fromkeys(complementary_assets)
        )

        conflicting_assets = list(
            dict.fromkeys(conflicting_assets)
        )

        if complementary_assets:
            score += min(
                1.0,
                0.5 * len(complementary_assets),
            )
            reasons.append("composition_relationship")

        if conflicting_assets:
            score = 0.0
            reasons.append("composition_conflict")

        if asset.lifecycle == "deprecated":
            score = 0.0

        score = round(
            min(self.MAX_SCORE, score),
            6,
        )

        compatible = (
            score >= self.COMPATIBILITY_THRESHOLD
            and not conflicting_assets
            and asset.lifecycle != "deprecated"
        )

        return CompositionCompatibilityResult(
            asset_id=asset.id,
            compatible=compatible,
            score=score,
            reasons=tuple(dict.fromkeys(reasons)),
            missing_dependencies=tuple(
                dict.fromkeys(missing_dependencies)
            ),
            conflicting_assets=tuple(
                dict.fromkeys(conflicting_assets)
            ),
            complementary_assets=tuple(
                dict.fromkeys(complementary_assets)
            ),
            metadata=self._metadata(asset),
        )

    def analyze_asset(
        self,
        asset_id: str,
        context: CompositionContext,
    ) -> CompositionCompatibilityResult:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        return self.analyze(asset, context)

    def analyze_all(
        self,
        context: CompositionContext,
    ) -> tuple[CompositionCompatibilityResult, ...]:
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
        context: CompositionContext,
    ) -> tuple[CompositionCompatibilityResult, ...]:
        return tuple(
            result
            for result in self.analyze_all(context)
            if result.compatible
        )

    @staticmethod
    def _metadata(
        asset: CodeAsset,
    ) -> dict[str, Any]:
        return {
            "name": asset.name,
            "asset_type": asset.asset_type,
            "language": asset.language,
            "framework": asset.framework,
            "runtime": asset.runtime,
            "version": asset.version,
            "lifecycle": asset.lifecycle,
        }


composition_compatibility = (
    CodeLibraryCompositionCompatibilityEngine()
)


__all__ = (
    "CompositionContext",
    "CompositionCompatibilityResult",
    "CodeLibraryCompositionCompatibilityEngine",
    "composition_compatibility",
)
