from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAsset
from .success_rates import CodeLibrarySuccessRateCalculator
from .validation_tracking import CodeLibraryValidationTracker
from .repair_tracking import CodeLibraryRepairTracker
from .reuse_tracking import CodeLibraryReuseTracker


@dataclass(frozen=True)
class CodeAssetQualityScore:
    """Deterministic CL-10.1 quality projection for one asset."""

    asset_id: str
    score: float
    success_component: float
    validation_component: float
    repair_component: float
    reuse_component: float
    provenance_component: float
    completeness_component: float
    sample_size: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "score": self.score,
            "success_component": self.success_component,
            "validation_component": self.validation_component,
            "repair_component": self.repair_component,
            "reuse_component": self.reuse_component,
            "provenance_component": self.provenance_component,
            "completeness_component": self.completeness_component,
            "sample_size": self.sample_size,
        }


class CodeLibraryQualityScorer:
    """CL-10.1 asset quality scoring engine.

    This component calculates quality only. It does not promote, demote,
    deprecate, or otherwise mutate asset lifecycle state.
    """

    SUCCESS_WEIGHT = 0.35
    VALIDATION_WEIGHT = 0.20
    REPAIR_WEIGHT = 0.15
    REUSE_WEIGHT = 0.10
    PROVENANCE_WEIGHT = 0.10
    COMPLETENESS_WEIGHT = 0.10

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        success_rates: CodeLibrarySuccessRateCalculator | None = None,
        validation: CodeLibraryValidationTracker | None = None,
        repairs: CodeLibraryRepairTracker | None = None,
        reuse: CodeLibraryReuseTracker | None = None,
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
        self.reuse = (
            reuse
            or CodeLibraryReuseTracker(self.engine)
        )

    def calculate(
        self,
        asset_id: str,
    ) -> CodeAssetQualityScore:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        success = self.success_rates.calculate(asset_id)
        validation = self.validation.summary(asset_id)
        repairs = self.repairs.summary(asset_id)
        reuse = self.reuse.summary(asset_id)

        success_component = success.success_rate

        validation_component = (
            validation.pass_rate
            if validation.validations > 0
            else 0.0
        )

        repair_component = (
            1.0 / (1.0 + repairs.average_repairs_per_repaired_build)
            if repairs.repaired_builds > 0
            else 1.0
        )

        reuse_component = (
            min(1.0, reuse.total_reuses / 3.0)
            if reuse.total_reuses > 0
            else 0.0
        )

        provenance_component = self._provenance_score(asset)

        completeness_component = self._completeness_score(asset)

        score = (
            success_component * self.SUCCESS_WEIGHT
            + validation_component * self.VALIDATION_WEIGHT
            + repair_component * self.REPAIR_WEIGHT
            + reuse_component * self.REUSE_WEIGHT
            + provenance_component * self.PROVENANCE_WEIGHT
            + completeness_component * self.COMPLETENESS_WEIGHT
        )

        sample_size = (
            success.total_builds
            + validation.validations
            + repairs.repair_events
            + reuse.reuse_events
        )

        return CodeAssetQualityScore(
            asset_id=asset_id,
            score=max(0.0, min(1.0, score)),
            success_component=success_component,
            validation_component=validation_component,
            repair_component=repair_component,
            reuse_component=reuse_component,
            provenance_component=provenance_component,
            completeness_component=completeness_component,
            sample_size=sample_size,
        )

    def calculate_many(
        self,
        asset_ids: list[str],
    ) -> tuple[CodeAssetQualityScore, ...]:
        return tuple(
            self.calculate(asset_id)
            for asset_id in asset_ids
        )

    def calculate_all(self) -> tuple[CodeAssetQualityScore, ...]:
        return self.calculate_many(
            [asset.id for asset in self.engine.list_assets()]
        )

    @staticmethod
    def _provenance_score(asset: CodeAsset) -> float:
        provenance = asset.provenance

        fields = (
            provenance.source,
            provenance.source_type,
            provenance.reference,
        )

        return sum(bool(value.strip()) for value in fields) / len(fields)

    @staticmethod
    def _completeness_score(asset: CodeAsset) -> float:
        checks = (
            bool(asset.name.strip()),
            bool(asset.description.strip()),
            bool(asset.language.strip()),
            bool(asset.framework.strip()),
            bool(asset.runtime.strip()),
            bool(asset.files),
            bool(asset.capabilities),
            bool(asset.dependencies),
            bool(asset.entrypoints),
        )

        return sum(checks) / len(checks)


quality_scorer = CodeLibraryQualityScorer()


__all__ = (
    "CodeAssetQualityScore",
    "CodeLibraryQualityScorer",
    "quality_scorer",
)
