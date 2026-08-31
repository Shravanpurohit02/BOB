from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import CodeAsset
from .engine import CodeLibraryEngine
from .recommendation import (
    CodeAssetRecommendation,
    CodeLibraryRecommendationEngine,
    CodeAssetRecommendationRequest,
)


@dataclass(frozen=True)
class AssetRecommendationContext:
    """Project context used to refine Code Library recommendations."""

    project_id: str = ""
    project_name: str = ""
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
    query: str = ""
    limit: int = 10
    include_deprecated: bool = False


class ContextAwareRecommendationEngine:
    """Recommendation engine that incorporates project context."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.base = CodeLibraryRecommendationEngine(self.engine)

    def recommend(
        self,
        context: AssetRecommendationContext,
    ) -> tuple[CodeAssetRecommendation, ...]:
        if context.limit < 1:
            raise ValueError(
                "Recommendation limit must be at least 1"
            )

        request = CodeAssetRecommendationRequest(
            query=context.query,
            asset_type=context.asset_type,
            language=context.language,
            framework=context.framework,
            runtime=context.runtime,
            tags=context.tags,
            capabilities=context.capabilities,
            dependencies=context.dependencies,
            limit=max(context.limit, len(self.engine.list_assets())),
            include_deprecated=context.include_deprecated,
        )

        base_results = self.base.recommend(request)

        existing_ids = set(context.existing_asset_ids)
        existing_capabilities = {
            value.strip().lower()
            for value in context.existing_capabilities
            if value.strip()
        }
        existing_dependencies = {
            value.strip().lower()
            for value in context.existing_dependencies
            if value.strip()
        }

        ranked: list[CodeAssetRecommendation] = []

        for result in base_results:
            if result.asset_id in existing_ids:
                continue

            asset = self.engine.get(result.asset_id)

            if asset is None:
                continue

            score = result.score
            reasons = list(result.reasons)

            capability_overlap = (
                {
                    value.strip().lower()
                    for value in asset.capabilities
                }
                & existing_capabilities
            )

            dependency_overlap = (
                {
                    value.strip().lower()
                    for value in asset.dependencies
                }
                & existing_dependencies
            )

            if capability_overlap:
                score += 2.0 * len(capability_overlap)
                reasons.extend(
                    f"existing_capability:{value}"
                    for value in sorted(capability_overlap)
                )

            if dependency_overlap:
                score += 0.5 * len(dependency_overlap)
                reasons.extend(
                    f"existing_dependency:{value}"
                    for value in sorted(dependency_overlap)
                )

            if (
                context.project_name
                and context.project_name.lower()
                in asset.name.lower()
            ):
                score += 1.0
                reasons.append("project_name_match")

            ranked.append(
                CodeAssetRecommendation(
                    asset_id=result.asset_id,
                    score=round(score, 6),
                    reasons=tuple(dict.fromkeys(reasons)),
                    metadata={
                        **dict(result.metadata or {}),
                        "context_project_id": context.project_id,
                        "context_project_name": context.project_name,
                    },
                )
            )

        ranked.sort(
            key=lambda item: (
                -item.score,
                item.asset_id,
            )
        )

        return tuple(ranked[: context.limit])

    def recommend_for_project(
        self,
        *,
        project_id: str = "",
        project_name: str = "",
        language: str = "",
        framework: str = "",
        runtime: str = "",
        asset_type: str = "",
        tags: tuple[str, ...] = (),
        capabilities: tuple[str, ...] = (),
        dependencies: tuple[str, ...] = (),
        existing_asset_ids: tuple[str, ...] = (),
        existing_capabilities: tuple[str, ...] = (),
        existing_dependencies: tuple[str, ...] = (),
        query: str = "",
        limit: int = 10,
        include_deprecated: bool = False,
    ) -> tuple[CodeAssetRecommendation, ...]:
        return self.recommend(
            AssetRecommendationContext(
                project_id=project_id,
                project_name=project_name,
                language=language,
                framework=framework,
                runtime=runtime,
                asset_type=asset_type,
                tags=tags,
                capabilities=capabilities,
                dependencies=dependencies,
                existing_asset_ids=existing_asset_ids,
                existing_capabilities=existing_capabilities,
                existing_dependencies=existing_dependencies,
                query=query,
                limit=limit,
                include_deprecated=include_deprecated,
            )
        )


context_recommendation = ContextAwareRecommendationEngine()


__all__ = (
    "AssetRecommendationContext",
    "ContextAwareRecommendationEngine",
    "context_recommendation",
)
