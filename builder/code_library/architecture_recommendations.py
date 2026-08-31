from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .application_stacks import (
    ApplicationStackContext,
    CodeLibraryApplicationStackEngine,
)
from .composition_planning import (
    CompositionPlanContext,
    CodeLibraryCompositionPlanningEngine,
)
from .models import CodeAsset


@dataclass(frozen=True)
class ArchitectureRecommendationContext:
    language: str = ""
    framework: str = ""
    runtime: str = ""
    asset_type: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    project_id: str = ""

    def key(self) -> str:
        return "|".join(
            (
                self.language.strip().lower(),
                self.framework.strip().lower(),
                self.runtime.strip().lower(),
                self.asset_type.strip().lower(),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.capabilities
                        if value.strip()
                    )
                ),
                ",".join(
                    sorted(
                        value.strip().lower()
                        for value in self.dependencies
                        if value.strip()
                    )
                ),
            )
        )

    def to_stack_context(self) -> ApplicationStackContext:
        return ApplicationStackContext(
            language=self.language,
            framework=self.framework,
            runtime=self.runtime,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
            project_id=self.project_id,
        )

    def to_composition_context(self) -> CompositionPlanContext:
        return CompositionPlanContext(
            language=self.language,
            framework=self.framework,
            runtime=self.runtime,
            asset_type=self.asset_type,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
        )

    def to_dict(self) -> dict:
        return {
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "asset_type": self.asset_type,
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "project_id": self.project_id,
            "context_key": self.key(),
        }


@dataclass(frozen=True)
class ArchitectureRecommendation:
    recommendation_id: str
    asset_ids: tuple[str, ...]
    source: str
    score: float
    confidence: float
    success_rate: float
    reusable: bool
    reasons: tuple[str, ...] = ()
    metadata: dict[str, object] | None = None

    def __post_init__(self) -> None:
        if not self.recommendation_id.strip():
            raise ValueError(
                "recommendation_id must not be empty"
            )

        normalized = tuple(
            sorted(
                dict.fromkeys(
                    asset_id.strip()
                    for asset_id in self.asset_ids
                    if asset_id and asset_id.strip()
                )
            )
        )

        if not normalized:
            raise ValueError(
                "asset_ids must contain at least one asset"
            )

        if not 0.0 <= self.score <= 10.0:
            raise ValueError(
                "score must be between 0.0 and 10.0"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError(
                "success_rate must be between 0.0 and 1.0"
            )

        object.__setattr__(
            self,
            "asset_ids",
            normalized,
        )

    def to_dict(self) -> dict:
        return {
            "recommendation_id": self.recommendation_id,
            "asset_ids": list(self.asset_ids),
            "source": self.source,
            "score": self.score,
            "confidence": self.confidence,
            "success_rate": self.success_rate,
            "reusable": self.reusable,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryArchitectureRecommendationEngine:
    """
    Produces architecture recommendations from reusable application
    stacks and composition intelligence.

    The engine is deliberately advisory. It does not mutate the code
    library and does not silently select or assemble assets.
    """

    def __init__(
        self,
        *,
        stack_engine: CodeLibraryApplicationStackEngine | None = None,
        composition_engine: CodeLibraryCompositionPlanningEngine | None = None,
    ) -> None:
        self.stack_engine = (
            stack_engine
            or CodeLibraryApplicationStackEngine()
        )
        self.composition_engine = composition_engine

    @staticmethod
    def normalize_asset_ids(
        asset_ids: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = tuple(
            sorted(
                dict.fromkeys(
                    asset_id.strip()
                    for asset_id in asset_ids
                    if asset_id and asset_id.strip()
                )
            )
        )

        if not normalized:
            raise ValueError(
                "asset_ids must contain at least one asset"
            )

        return normalized

    def recommend_from_stacks(
        self,
        *,
        context: ArchitectureRecommendationContext | None = None,
        minimum_observations: int = 1,
        minimum_success_rate: float = 0.6,
    ) -> tuple[ArchitectureRecommendation, ...]:
        context = (
            context
            or ArchitectureRecommendationContext()
        )

        results = self.stack_engine.reusable_stacks(
            context=context.to_stack_context(),
            minimum_observations=minimum_observations,
            minimum_success_rate=minimum_success_rate,
        )

        recommendations = []

        for result in results:
            score = min(
                10.0,
                (
                    result.average_score * 0.55
                    + result.success_rate * 3.0
                    + result.confidence * 2.0
                ),
            )

            reasons = [
                "reusable_stack",
                "successful_history",
            ]

            if result.confidence >= 0.8:
                reasons.append(
                    "high_confidence"
                )
            elif result.confidence >= 0.4:
                reasons.append(
                    "moderate_confidence"
                )

            recommendations.append(
                ArchitectureRecommendation(
                    recommendation_id=(
                        f"stack:{result.stack_id}"
                    ),
                    asset_ids=result.asset_ids,
                    source="reusable_stack",
                    score=round(score, 4),
                    confidence=result.confidence,
                    success_rate=result.success_rate,
                    reusable=True,
                    reasons=tuple(reasons),
                    metadata={
                        "stack_id": result.stack_id,
                        "observation_count": (
                            result.observation_count
                        ),
                        "average_score": (
                            result.average_score
                        ),
                        "context_key": result.context_key,
                    },
                )
            )

        return tuple(
            sorted(
                recommendations,
                key=lambda recommendation: (
                    -recommendation.score,
                    -recommendation.confidence,
                    -recommendation.success_rate,
                    recommendation.recommendation_id,
                ),
            )
        )

    def recommend(
        self,
        *,
        context: ArchitectureRecommendationContext | None = None,
        minimum_observations: int = 1,
        minimum_success_rate: float = 0.6,
        limit: int | None = None,
    ) -> tuple[ArchitectureRecommendation, ...]:
        if limit is not None and limit < 1:
            raise ValueError(
                "limit must be at least 1"
            )

        recommendations = self.recommend_from_stacks(
            context=context,
            minimum_observations=minimum_observations,
            minimum_success_rate=minimum_success_rate,
        )

        if limit is not None:
            return recommendations[:limit]

        return recommendations

    def recommend_for_assets(
        self,
        asset_ids: Iterable[str],
        *,
        context: ArchitectureRecommendationContext | None = None,
    ) -> tuple[ArchitectureRecommendation, ...]:
        context = (
            context
            or ArchitectureRecommendationContext()
        )

        normalized = self.normalize_asset_ids(asset_ids)

        matches = self.stack_engine.stack_for_assets(
            normalized,
            context=context.to_stack_context(),
        )

        recommendations = []

        for result in matches:
            score = min(
                10.0,
                (
                    result.average_score * 0.6
                    + result.success_rate * 2.5
                    + result.confidence * 2.0
                ),
            )

            recommendations.append(
                ArchitectureRecommendation(
                    recommendation_id=(
                        f"asset-match:{result.stack_id}"
                    ),
                    asset_ids=result.asset_ids,
                    source="asset_match",
                    score=round(score, 4),
                    confidence=result.confidence,
                    success_rate=result.success_rate,
                    reusable=result.reusable,
                    reasons=(
                        "asset_set_match",
                        "reusable_stack",
                    ),
                    metadata={
                        "stack_id": result.stack_id,
                        "context_key": result.context_key,
                    },
                )
            )

        return tuple(
            sorted(
                recommendations,
                key=lambda recommendation: (
                    -recommendation.score,
                    recommendation.recommendation_id,
                ),
            )
        )

    def best(
        self,
        *,
        context: ArchitectureRecommendationContext | None = None,
        minimum_observations: int = 1,
        minimum_success_rate: float = 0.6,
    ) -> ArchitectureRecommendation | None:
        recommendations = self.recommend(
            context=context,
            minimum_observations=minimum_observations,
            minimum_success_rate=minimum_success_rate,
            limit=1,
        )

        return (
            recommendations[0]
            if recommendations
            else None
        )

    def to_dict(
        self,
        *,
        context: ArchitectureRecommendationContext | None = None,
    ) -> dict:
        context = (
            context
            or ArchitectureRecommendationContext()
        )

        recommendations = self.recommend(
            context=context
        )

        return {
            "context": context.to_dict(),
            "recommendations": [
                recommendation.to_dict()
                for recommendation in recommendations
            ],
            "recommendation_count": len(
                recommendations
            ),
        }
