from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAsset


@dataclass(frozen=True)
class AssetConflictContext:
    """Project state used for asset conflict analysis."""

    existing_asset_ids: tuple[str, ...] = ()
    existing_names: tuple[str, ...] = ()
    existing_dependencies: tuple[str, ...] = ()
    existing_capabilities: tuple[str, ...] = ()
    language: str = ""
    framework: str = ""
    runtime: str = ""
    asset_type: str = ""


@dataclass(frozen=True)
class AssetConflictResult:
    """Conflict analysis result for one Code Library asset."""

    asset_id: str
    conflicted: bool
    severity: str
    reasons: tuple[str, ...] = ()
    conflicting_assets: tuple[str, ...] = ()
    conflicting_dependencies: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "conflicted": self.conflicted,
            "severity": self.severity,
            "reasons": list(self.reasons),
            "conflicting_assets": list(self.conflicting_assets),
            "conflicting_dependencies": list(
                self.conflicting_dependencies
            ),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryConflictAnalysisEngine:
    """Detects identity, framework, dependency, and lifecycle conflicts."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def analyze(
        self,
        asset: CodeAsset,
        context: AssetConflictContext,
    ) -> AssetConflictResult:
        reasons: list[str] = []
        conflicting_assets: list[str] = []
        conflicting_dependencies: list[str] = []

        existing_ids = set(context.existing_asset_ids)

        if asset.id in existing_ids:
            reasons.append("duplicate_identity")
            conflicting_assets.append(asset.id)

        existing_names = {
            value.strip().lower()
            for value in context.existing_names
            if value.strip()
        }

        if asset.name.strip().lower() in existing_names:
            reasons.append("duplicate_name")
            conflicting_assets.append(asset.id)

        if context.language and asset.language:
            if asset.language.lower() != context.language.lower():
                reasons.append("language_conflict")

        if context.framework and asset.framework:
            if asset.framework.lower() != context.framework.lower():
                reasons.append("framework_conflict")

        if context.runtime and asset.runtime:
            if asset.runtime.lower() != context.runtime.lower():
                reasons.append("runtime_conflict")

        if context.asset_type:
            if asset.asset_type != context.asset_type:
                reasons.append("asset_type_conflict")

        project_dependencies = {
            value.strip().lower()
            for value in context.existing_dependencies
            if value.strip()
        }

        asset_dependencies = {
            value.strip().lower()
            for value in asset.dependencies
            if value.strip()
        }

        dependency_overlap = (
            project_dependencies & asset_dependencies
        )

        if dependency_overlap:
            conflicting_dependencies.extend(
                sorted(dependency_overlap)
            )
            reasons.append("dependency_overlap")

        project_capabilities = {
            value.strip().lower()
            for value in context.existing_capabilities
            if value.strip()
        }

        asset_capabilities = {
            value.strip().lower()
            for value in asset.capabilities
            if value.strip()
        }

        capability_overlap = (
            project_capabilities & asset_capabilities
        )

        if capability_overlap:
            reasons.append("capability_overlap")

        if asset.lifecycle == "deprecated":
            reasons.append("deprecated_asset")

        if conflicting_assets:
            severity = "critical"
        elif "framework_conflict" in reasons:
            severity = "high"
        elif (
            "runtime_conflict" in reasons
            or "language_conflict" in reasons
            or "asset_type_conflict" in reasons
        ):
            severity = "medium"
        elif (
            "dependency_overlap" in reasons
            or "capability_overlap" in reasons
            or "deprecated_asset" in reasons
        ):
            severity = "low"
        else:
            severity = "none"

        return AssetConflictResult(
            asset_id=asset.id,
            conflicted=bool(reasons),
            severity=severity,
            reasons=tuple(dict.fromkeys(reasons)),
            conflicting_assets=tuple(
                dict.fromkeys(conflicting_assets)
            ),
            conflicting_dependencies=tuple(
                dict.fromkeys(conflicting_dependencies)
            ),
            metadata=self._metadata(asset),
        )

    def analyze_asset(
        self,
        asset_id: str,
        context: AssetConflictContext,
    ) -> AssetConflictResult:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        return self.analyze(asset, context)

    def analyze_all(
        self,
        context: AssetConflictContext,
    ) -> tuple[AssetConflictResult, ...]:
        results = tuple(
            self.analyze(asset, context)
            for asset in self.engine.list_assets()
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    self._severity_rank(item.severity),
                    item.asset_id,
                ),
            )
        )

    def conflict_free_assets(
        self,
        context: AssetConflictContext,
    ) -> tuple[AssetConflictResult, ...]:
        return tuple(
            result
            for result in self.analyze_all(context)
            if not result.conflicted
        )

    @staticmethod
    def _severity_rank(severity: str) -> int:
        return {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
            "none": 4,
        }.get(severity, 5)

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


conflict_analysis = CodeLibraryConflictAnalysisEngine()


__all__ = (
    "AssetConflictContext",
    "AssetConflictResult",
    "CodeLibraryConflictAnalysisEngine",
    "conflict_analysis",
)
