from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAssetLifecycle
from .quality_scoring import CodeLibraryQualityScorer
from .reliability_scoring import CodeLibraryReliabilityScorer
from .success_detection import CodeLibrarySuccessDetector


@dataclass(frozen=True)
class CodeAssetPromotionDecision:
    """Deterministic CL-10.3 promotion decision."""

    asset_id: str
    eligible: bool
    quality_score: float
    reliability_score: float
    success_rate: float
    total_builds: int
    minimum_builds: int
    minimum_quality_score: float
    minimum_reliability_score: float
    minimum_success_rate: float
    lifecycle: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "eligible": self.eligible,
            "quality_score": self.quality_score,
            "reliability_score": self.reliability_score,
            "success_rate": self.success_rate,
            "total_builds": self.total_builds,
            "minimum_builds": self.minimum_builds,
            "minimum_quality_score": self.minimum_quality_score,
            "minimum_reliability_score": self.minimum_reliability_score,
            "minimum_success_rate": self.minimum_success_rate,
            "lifecycle": self.lifecycle,
            "reasons": list(self.reasons),
        }


class CodeLibraryPromotionRules:
    """CL-10.3 promotion eligibility engine.

    This component evaluates eligibility only. It does not mutate lifecycle
    state. Actual promotion remains an explicit lifecycle operation.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        quality: CodeLibraryQualityScorer | None = None,
        reliability: CodeLibraryReliabilityScorer | None = None,
        success_detector: CodeLibrarySuccessDetector | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.quality = quality or CodeLibraryQualityScorer(self.engine)
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
        minimum_quality_score: float = 0.70,
        minimum_reliability_score: float = 0.70,
        minimum_success_rate: float = 0.80,
    ) -> CodeAssetPromotionDecision:
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
            reasons.append("asset_is_deprecated")

        if quality.score < minimum_quality_score:
            reasons.append("quality_score_below_threshold")

        if reliability.score < minimum_reliability_score:
            reasons.append("reliability_score_below_threshold")

        if success.total_builds < minimum_builds:
            reasons.append("insufficient_build_history")

        if success.success_rate < minimum_success_rate:
            reasons.append("success_rate_below_threshold")

        eligible = not reasons

        if eligible:
            reasons.append("promotion_criteria_satisfied")

        return CodeAssetPromotionDecision(
            asset_id=asset_id,
            eligible=eligible,
            quality_score=quality.score,
            reliability_score=reliability.score,
            success_rate=success.success_rate,
            total_builds=success.total_builds,
            minimum_builds=minimum_builds,
            minimum_quality_score=minimum_quality_score,
            minimum_reliability_score=minimum_reliability_score,
            minimum_success_rate=minimum_success_rate,
            lifecycle=asset.lifecycle,
            reasons=tuple(reasons),
        )

    def eligible(
        self,
        asset_id: str,
        *,
        minimum_builds: int = 3,
        minimum_quality_score: float = 0.70,
        minimum_reliability_score: float = 0.70,
        minimum_success_rate: float = 0.80,
    ) -> bool:
        return self.evaluate(
            asset_id,
            minimum_builds=minimum_builds,
            minimum_quality_score=minimum_quality_score,
            minimum_reliability_score=minimum_reliability_score,
            minimum_success_rate=minimum_success_rate,
        ).eligible

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


promotion_rules = CodeLibraryPromotionRules()


__all__ = (
    "CodeAssetPromotionDecision",
    "CodeLibraryPromotionRules",
    "promotion_rules",
)
