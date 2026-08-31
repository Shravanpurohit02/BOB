from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAssetLifecycle
from .quality_scoring import CodeLibraryQualityScorer
from .reliability_scoring import CodeLibraryReliabilityScorer
from .success_detection import CodeLibrarySuccessDetector


@dataclass(frozen=True)
class CodeAssetDemotionDecision:
    """Deterministic CL-10.5 automatic-demotion decision."""

    asset_id: str
    should_demote: bool
    quality_score: float
    reliability_score: float
    success_rate: float
    total_builds: int
    minimum_quality_score: float
    minimum_reliability_score: float
    minimum_success_rate: float
    lifecycle: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "should_demote": self.should_demote,
            "quality_score": self.quality_score,
            "reliability_score": self.reliability_score,
            "success_rate": self.success_rate,
            "total_builds": self.total_builds,
            "minimum_quality_score": self.minimum_quality_score,
            "minimum_reliability_score": self.minimum_reliability_score,
            "minimum_success_rate": self.minimum_success_rate,
            "lifecycle": self.lifecycle,
            "reasons": list(self.reasons),
        }


class CodeLibraryDemotionRules:
    """CL-10.5 automatic-demotion evaluation engine.

    Demotion is deliberately limited to lifecycle states where an automatic
    downgrade is meaningful. The evaluator itself does not mutate assets;
    apply() performs the explicit lifecycle transition.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        quality: CodeLibraryQualityScorer | None = None,
        reliability: CodeLibraryReliabilityScorer | None = None,
        success_detector: CodeLibrarySuccessDetector | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

        self.quality = (
            quality
            or CodeLibraryQualityScorer(self.engine)
        )

        self.reliability = (
            reliability
            or CodeLibraryReliabilityScorer(
                self.engine,
                quality=self.quality,
            )
        )

        self.success_detector = (
            success_detector
            or CodeLibrarySuccessDetector(self.engine)
        )

    def evaluate(
        self,
        asset_id: str,
        *,
        minimum_builds: int = 3,
        minimum_quality_score: float = 0.50,
        minimum_reliability_score: float = 0.50,
        minimum_success_rate: float = 0.60,
    ) -> CodeAssetDemotionDecision:
        self._validate_thresholds(
            minimum_builds,
            minimum_quality_score,
            minimum_reliability_score,
            minimum_success_rate,
        )

        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        quality = self.quality.calculate(asset_id)
        reliability = self.reliability.calculate(asset_id)
        success = self.success_detector.detect(
            asset_id,
            minimum_builds=minimum_builds,
            minimum_success_rate=minimum_success_rate,
        )

        reasons: list[str] = []

        if asset.lifecycle == CodeAssetLifecycle.DEPRECATED.value:
            reasons.append("asset_already_deprecated")

        if asset.lifecycle not in {
            CodeAssetLifecycle.PROMOTED.value,
        }:
            reasons.append("asset_not_promoted")

        if quality.score < minimum_quality_score:
            reasons.append("quality_score_below_threshold")

        if reliability.score < minimum_reliability_score:
            reasons.append(
                "reliability_score_below_threshold"
            )

        if success.total_builds < minimum_builds:
            reasons.append("insufficient_build_history")

        if success.success_rate < minimum_success_rate:
            reasons.append("success_rate_below_threshold")

        should_demote = (
            asset.lifecycle == CodeAssetLifecycle.PROMOTED.value
            and any(
                reason in {
                    "quality_score_below_threshold",
                    "reliability_score_below_threshold",
                    "success_rate_below_threshold",
                }
                for reason in reasons
            )
        )

        if should_demote:
            reasons.append("automatic_demotion_criteria_satisfied")

        return CodeAssetDemotionDecision(
            asset_id=asset_id,
            should_demote=should_demote,
            quality_score=quality.score,
            reliability_score=reliability.score,
            success_rate=success.success_rate,
            total_builds=success.total_builds,
            minimum_quality_score=minimum_quality_score,
            minimum_reliability_score=minimum_reliability_score,
            minimum_success_rate=minimum_success_rate,
            lifecycle=asset.lifecycle,
            reasons=tuple(reasons),
        )

    def apply(
        self,
        asset_id: str,
        *,
        minimum_builds: int = 3,
        minimum_quality_score: float = 0.50,
        minimum_reliability_score: float = 0.50,
        minimum_success_rate: float = 0.60,
    ):
        decision = self.evaluate(
            asset_id,
            minimum_builds=minimum_builds,
            minimum_quality_score=minimum_quality_score,
            minimum_reliability_score=minimum_reliability_score,
            minimum_success_rate=minimum_success_rate,
        )

        if not decision.should_demote:
            return self.engine.get(asset_id)

        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        # Existing lifecycle rules determine the legal target state.
        return self.engine.deprecate(asset.id)

    @staticmethod
    def _validate_thresholds(
        minimum_builds: int,
        minimum_quality_score: float,
        minimum_reliability_score: float,
        minimum_success_rate: float,
    ) -> None:
        if minimum_builds < 1:
            raise ValueError(
                "minimum_builds must be at least 1"
            )

        for name, value in (
            ("minimum_quality_score", minimum_quality_score),
            ("minimum_reliability_score", minimum_reliability_score),
            ("minimum_success_rate", minimum_success_rate),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0 and 1"
                )


demotion_rules = CodeLibraryDemotionRules()


__all__ = (
    "CodeAssetDemotionDecision",
    "CodeLibraryDemotionRules",
    "demotion_rules",
)
