from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .quality_scoring import CodeLibraryQualityScorer
from .success_rates import CodeLibrarySuccessRateCalculator
from .validation_tracking import CodeLibraryValidationTracker
from .repair_tracking import CodeLibraryRepairTracker


@dataclass(frozen=True)
class CodeAssetReliabilityScore:
    """Deterministic CL-10.2 reliability projection for one asset."""

    asset_id: str
    score: float
    success_rate: float
    validation_pass_rate: float
    repair_stability: float
    quality_score: float
    sample_size: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "score": self.score,
            "success_rate": self.success_rate,
            "validation_pass_rate": self.validation_pass_rate,
            "repair_stability": self.repair_stability,
            "quality_score": self.quality_score,
            "sample_size": self.sample_size,
        }


class CodeLibraryReliabilityScorer:
    """CL-10.2 reliability scoring engine.

    Reliability measures repeatable construction behavior. It is analytical
    only and does not change lifecycle or promotion state.
    """

    SUCCESS_WEIGHT = 0.40
    VALIDATION_WEIGHT = 0.25
    REPAIR_WEIGHT = 0.20
    QUALITY_WEIGHT = 0.15

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        success_rates: CodeLibrarySuccessRateCalculator | None = None,
        validation: CodeLibraryValidationTracker | None = None,
        repairs: CodeLibraryRepairTracker | None = None,
        quality: CodeLibraryQualityScorer | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.success_rates = (
            success_rates
            or CodeLibrarySuccessRateCalculator(self.engine)
        )
        self.validation = (
            validation
            or CodeLibraryValidationTracker(self.engine)
        )
        self.repairs = (
            repairs
            or CodeLibraryRepairTracker(self.engine)
        )
        self.quality = (
            quality
            or CodeLibraryQualityScorer(
                self.engine,
                self.success_rates,
                self.validation,
                self.repairs,
            )
        )

    def calculate(
        self,
        asset_id: str,
    ) -> CodeAssetReliabilityScore:
        if self.engine.get(asset_id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        success = self.success_rates.calculate(asset_id)
        validation = self.validation.summary(asset_id)
        repairs = self.repairs.summary(asset_id)
        quality = self.quality.calculate(asset_id)

        success_rate = success.success_rate

        validation_pass_rate = (
            validation.pass_rate
            if validation.validations > 0
            else 0.0
        )

        repair_stability = (
            1.0 / (
                1.0
                + repairs.average_repairs_per_repaired_build
            )
            if repairs.repaired_builds > 0
            else 1.0
        )

        score = (
            success_rate * self.SUCCESS_WEIGHT
            + validation_pass_rate * self.VALIDATION_WEIGHT
            + repair_stability * self.REPAIR_WEIGHT
            + quality.score * self.QUALITY_WEIGHT
        )

        sample_size = (
            success.total_builds
            + validation.validations
            + repairs.repair_events
        )

        return CodeAssetReliabilityScore(
            asset_id=asset_id,
            score=max(0.0, min(1.0, score)),
            success_rate=success_rate,
            validation_pass_rate=validation_pass_rate,
            repair_stability=repair_stability,
            quality_score=quality.score,
            sample_size=sample_size,
        )

    def calculate_many(
        self,
        asset_ids: list[str],
    ) -> tuple[CodeAssetReliabilityScore, ...]:
        return tuple(
            self.calculate(asset_id)
            for asset_id in asset_ids
        )

    def calculate_all(
        self,
    ) -> tuple[CodeAssetReliabilityScore, ...]:
        return self.calculate_many(
            [asset.id for asset in self.engine.list_assets()]
        )


reliability_scorer = CodeLibraryReliabilityScorer()


__all__ = (
    "CodeAssetReliabilityScore",
    "CodeLibraryReliabilityScorer",
    "reliability_scorer",
)
