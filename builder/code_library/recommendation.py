from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset


@dataclass(frozen=True)
class CodeAssetRecommendation:
    """Ranked recommendation for a Code Library asset."""

    asset_id: str
    score: float
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class CodeAssetRecommendationRequest:
    """Normalized request used by the recommendation engine."""

    query: str = ""
    asset_type: str = ""
    language: str = ""
    framework: str = ""
    runtime: str = ""
    tags: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    limit: int = 10
    include_deprecated: bool = False


class CodeLibraryRecommendationEngine:
    """Deterministic recommendation engine for Code Library assets."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def recommend(
        self,
        request: CodeAssetRecommendationRequest,
    ) -> tuple[CodeAssetRecommendation, ...]:
        if request.limit < 1:
            raise ValueError("Recommendation limit must be at least 1")

        candidates = self.engine.list_assets()
        ranked: list[CodeAssetRecommendation] = []

        for asset in candidates:
            if (
                not request.include_deprecated
                and asset.lifecycle == "deprecated"
            ):
                continue

            score, reasons = self._score(asset, request)

            if score <= 0:
                continue

            ranked.append(
                CodeAssetRecommendation(
                    asset_id=asset.id,
                    score=round(score, 6),
                    reasons=tuple(reasons),
                    metadata={
                        "name": asset.name,
                        "asset_type": asset.asset_type,
                        "version": asset.version,
                        "lifecycle": asset.lifecycle,
                    },
                )
            )

        ranked.sort(
            key=lambda item: (
                -item.score,
                item.asset_id,
            )
        )

        return tuple(ranked[: request.limit])

    def recommend_for_query(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> tuple[CodeAssetRecommendation, ...]:
        return self.recommend(
            CodeAssetRecommendationRequest(
                query=query,
                limit=limit,
            )
        )

    def recommend_all(
        self,
        *,
        limit: int = 10,
    ) -> tuple[CodeAssetRecommendation, ...]:
        return self.recommend(
            CodeAssetRecommendationRequest(
                limit=limit,
            )
        )

    @staticmethod
    def _score(
        asset: CodeAsset,
        request: CodeAssetRecommendationRequest,
    ) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        query = request.query.strip().lower()

        if query:
            searchable = " ".join(
                (
                    asset.id,
                    asset.name,
                    asset.description,
                    asset.asset_type,
                    asset.language,
                    asset.framework,
                    asset.runtime,
                    *asset.tags,
                    *asset.capabilities,
                )
            ).lower()

            if query in searchable:
                score += 5.0
                reasons.append("query_match")

            query_terms = {
                term
                for term in query.split()
                if term
            }

            for term in query_terms:
                if term in asset.name.lower():
                    score += 2.0
                    reasons.append("name_match")
                elif term in asset.tags:
                    score += 1.0
                    reasons.append("tag_match")
                elif term in asset.capabilities:
                    score += 1.0
                    reasons.append("capability_match")

        if request.asset_type:
            if asset.asset_type == request.asset_type:
                score += 3.0
                reasons.append("asset_type_match")
            else:
                return 0.0, []

        if request.language:
            if asset.language.lower() == request.language.lower():
                score += 2.0
                reasons.append("language_match")
            else:
                return 0.0, []

        if request.framework:
            if asset.framework.lower() == request.framework.lower():
                score += 2.0
                reasons.append("framework_match")
            else:
                return 0.0, []

        if request.runtime:
            if asset.runtime.lower() == request.runtime.lower():
                score += 1.5
                reasons.append("runtime_match")
            else:
                return 0.0, []

        requested_tags = {
            value.strip().lower()
            for value in request.tags
            if value.strip()
        }

        asset_tags = {
            value.strip().lower()
            for value in asset.tags
        }

        matched_tags = requested_tags & asset_tags

        if requested_tags and not matched_tags:
            return 0.0, []

        for tag in sorted(matched_tags):
            score += 1.0
            reasons.append(f"tag:{tag}")

        requested_capabilities = {
            value.strip().lower()
            for value in request.capabilities
            if value.strip()
        }

        asset_capabilities = {
            value.strip().lower()
            for value in asset.capabilities
        }

        matched_capabilities = (
            requested_capabilities & asset_capabilities
        )

        if requested_capabilities and not matched_capabilities:
            return 0.0, []

        for capability in sorted(matched_capabilities):
            score += 1.5
            reasons.append(f"capability:{capability}")

        requested_dependencies = {
            value.strip().lower()
            for value in request.dependencies
            if value.strip()
        }

        asset_dependencies = {
            value.strip().lower()
            for value in asset.dependencies
        }

        matched_dependencies = (
            requested_dependencies & asset_dependencies
        )

        if requested_dependencies and not matched_dependencies:
            return 0.0, []

        for dependency in sorted(matched_dependencies):
            score += 0.5
            reasons.append(f"dependency:{dependency}")

        if asset.lifecycle == "promoted":
            score += 2.0
            reasons.append("promoted")

        if asset.success_rate > 0:
            score += asset.success_rate
            reasons.append("success_rate")

        if not reasons and not query:
            score = 1.0
            reasons.append("available_asset")

        return score, reasons


recommendation = CodeLibraryRecommendationEngine()


__all__ = (
    "CodeAssetRecommendation",
    "CodeAssetRecommendationRequest",
    "CodeLibraryRecommendationEngine",
    "recommendation",
)
