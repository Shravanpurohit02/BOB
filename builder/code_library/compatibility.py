from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAsset


@dataclass(frozen=True)
class AssetCompatibilityContext:
    """Project characteristics used for compatibility evaluation."""

    language: str = ""
    framework: str = ""
    runtime: str = ""
    asset_type: str = ""
    tags: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    existing_asset_ids: tuple[str, ...] = ()
    existing_capabilities: tuple[str, ...] = ()
    existing_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssetCompatibilityScore:
    """Deterministic compatibility result for one asset."""

    asset_id: str
    score: float
    compatible: bool
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "score": self.score,
            "compatible": self.compatible,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryCompatibilityEngine:
    """Project-aware compatibility scorer for Code Library assets."""

    MAX_SCORE = 10.0
    COMPATIBILITY_THRESHOLD = 5.0

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def score(
        self,
        asset: CodeAsset,
        context: AssetCompatibilityContext,
    ) -> AssetCompatibilityScore:
        score = 0.0
        reasons: list[str] = []

        if asset.lifecycle == "deprecated":
            return AssetCompatibilityScore(
                asset_id=asset.id,
                score=0.0,
                compatible=False,
                reasons=("deprecated_asset",),
                metadata=self._metadata(asset),
            )

        if context.language:
            if asset.language.lower() != context.language.lower():
                return self._incompatible(
                    asset,
                    "language_mismatch",
                )
            score += 2.5
            reasons.append("language_match")

        if context.framework:
            if asset.framework.lower() != context.framework.lower():
                return self._incompatible(
                    asset,
                    "framework_mismatch",
                )
            score += 2.5
            reasons.append("framework_match")

        if context.runtime:
            if asset.runtime.lower() != context.runtime.lower():
                return self._incompatible(
                    asset,
                    "runtime_mismatch",
                )
            score += 1.5
            reasons.append("runtime_match")

        if context.asset_type:
            if asset.asset_type != context.asset_type:
                return self._incompatible(
                    asset,
                    "asset_type_mismatch",
                )
            score += 1.0
            reasons.append("asset_type_match")

        requested_tags = {
            value.strip().lower()
            for value in context.tags
            if value.strip()
        }
        asset_tags = {
            value.strip().lower()
            for value in asset.tags
        }

        if requested_tags:
            matched_tags = requested_tags & asset_tags
            if not matched_tags:
                return self._incompatible(
                    asset,
                    "tag_mismatch",
                )
            score += min(
                1.0,
                0.5 * len(matched_tags),
            )
            reasons.extend(
                f"tag_match:{value}"
                for value in sorted(matched_tags)
            )

        requested_capabilities = {
            value.strip().lower()
            for value in context.capabilities
            if value.strip()
        }
        asset_capabilities = {
            value.strip().lower()
            for value in asset.capabilities
        }

        if requested_capabilities:
            matched_capabilities = (
                requested_capabilities & asset_capabilities
            )
            if not matched_capabilities:
                return self._incompatible(
                    asset,
                    "capability_mismatch",
                )
            score += min(
                1.0,
                0.5 * len(matched_capabilities),
            )
            reasons.extend(
                f"capability_match:{value}"
                for value in sorted(matched_capabilities)
            )

        requested_dependencies = {
            value.strip().lower()
            for value in context.dependencies
            if value.strip()
        }
        asset_dependencies = {
            value.strip().lower()
            for value in asset.dependencies
        }

        if requested_dependencies:
            matched_dependencies = (
                requested_dependencies & asset_dependencies
            )
            if not matched_dependencies:
                return self._incompatible(
                    asset,
                    "dependency_mismatch",
                )
            score += min(
                0.5,
                0.25 * len(matched_dependencies),
            )
            reasons.extend(
                f"dependency_match:{value}"
                for value in sorted(matched_dependencies)
            )

        existing_ids = set(context.existing_asset_ids)

        if asset.id in existing_ids:
            return self._incompatible(
                asset,
                "already_present",
            )

        existing_capabilities = {
            value.strip().lower()
            for value in context.existing_capabilities
            if value.strip()
        }
        capability_overlap = (
            existing_capabilities & asset_capabilities
        )

        if capability_overlap:
            score += min(
                1.0,
                0.5 * len(capability_overlap),
            )
            reasons.extend(
                f"existing_capability:{value}"
                for value in sorted(capability_overlap)
            )

        existing_dependencies = {
            value.strip().lower()
            for value in context.existing_dependencies
            if value.strip()
        }
        dependency_overlap = (
            existing_dependencies & asset_dependencies
        )

        if dependency_overlap:
            score += min(
                0.5,
                0.25 * len(dependency_overlap),
            )
            reasons.extend(
                f"existing_dependency:{value}"
                for value in sorted(dependency_overlap)
            )

        score = round(
            min(self.MAX_SCORE, score),
            6,
        )

        return AssetCompatibilityScore(
            asset_id=asset.id,
            score=score,
            compatible=score >= self.COMPATIBILITY_THRESHOLD,
            reasons=tuple(reasons),
            metadata=self._metadata(asset),
        )

    def score_asset(
        self,
        asset_id: str,
        context: AssetCompatibilityContext,
    ) -> AssetCompatibilityScore:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        return self.score(asset, context)

    def score_all(
        self,
        context: AssetCompatibilityContext,
    ) -> tuple[AssetCompatibilityScore, ...]:
        results = tuple(
            self.score(asset, context)
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
        context: AssetCompatibilityContext,
    ) -> tuple[AssetCompatibilityScore, ...]:
        return tuple(
            result
            for result in self.score_all(context)
            if result.compatible
        )

    def _incompatible(
        self,
        asset: CodeAsset,
        reason: str,
    ) -> AssetCompatibilityScore:
        return AssetCompatibilityScore(
            asset_id=asset.id,
            score=0.0,
            compatible=False,
            reasons=(reason,),
            metadata=self._metadata(asset),
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


compatibility = CodeLibraryCompatibilityEngine()


__all__ = (
    "AssetCompatibilityContext",
    "AssetCompatibilityScore",
    "CodeLibraryCompatibilityEngine",
    "compatibility",
)
