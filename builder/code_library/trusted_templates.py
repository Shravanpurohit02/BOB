from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset
from .promotion import CodeLibraryPromotionRules
from .quality_scoring import CodeLibraryQualityScorer
from .reliability_scoring import CodeLibraryReliabilityScorer


@dataclass(frozen=True)
class CodeAssetTrustDecision:
    """Deterministic CL-10.4 trusted-template decision."""

    asset_id: str
    trusted: bool
    quality_score: float
    reliability_score: float
    lifecycle: str
    minimum_quality_score: float
    minimum_reliability_score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "trusted": self.trusted,
            "quality_score": self.quality_score,
            "reliability_score": self.reliability_score,
            "lifecycle": self.lifecycle,
            "minimum_quality_score": self.minimum_quality_score,
            "minimum_reliability_score": self.minimum_reliability_score,
            "reasons": list(self.reasons),
        }


class CodeLibraryTrustedTemplateRegistry:
    """CL-10.4 registry for trusted Code Library templates.

    Trust is derived from objective quality/reliability criteria and lifecycle
    state. This component does not modify lifecycle state automatically.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        quality: CodeLibraryQualityScorer | None = None,
        reliability: CodeLibraryReliabilityScorer | None = None,
        promotion: CodeLibraryPromotionRules | None = None,
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

        self.promotion = (
            promotion
            or CodeLibraryPromotionRules(
                self.engine,
                quality=self.quality,
                reliability=self.reliability,
            )
        )

        self._trusted: set[str] = set()

    def evaluate(
        self,
        asset_id: str,
        *,
        minimum_quality_score: float = 0.80,
        minimum_reliability_score: float = 0.80,
    ) -> CodeAssetTrustDecision:
        self._validate_thresholds(
            minimum_quality_score,
            minimum_reliability_score,
        )

        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        quality = self.quality.calculate(asset_id)
        reliability = self.reliability.calculate(asset_id)

        reasons: list[str] = []

        if asset.lifecycle == "deprecated":
            reasons.append("asset_is_deprecated")

        if asset.lifecycle != "promoted":
            reasons.append("asset_not_promoted")

        if quality.score < minimum_quality_score:
            reasons.append("quality_score_below_threshold")

        if reliability.score < minimum_reliability_score:
            reasons.append(
                "reliability_score_below_threshold"
            )

        trusted = not reasons

        if trusted:
            reasons.append("trusted_template_criteria_satisfied")

        return CodeAssetTrustDecision(
            asset_id=asset_id,
            trusted=trusted,
            quality_score=quality.score,
            reliability_score=reliability.score,
            lifecycle=asset.lifecycle,
            minimum_quality_score=minimum_quality_score,
            minimum_reliability_score=minimum_reliability_score,
            reasons=tuple(reasons),
        )

    def trust(
        self,
        asset_id: str,
        *,
        minimum_quality_score: float = 0.80,
        minimum_reliability_score: float = 0.80,
    ) -> CodeAssetTrustDecision:
        decision = self.evaluate(
            asset_id,
            minimum_quality_score=minimum_quality_score,
            minimum_reliability_score=minimum_reliability_score,
        )

        if decision.trusted:
            self._trusted.add(asset_id)
        else:
            self._trusted.discard(asset_id)

        return decision

    def is_trusted(self, asset_id: str) -> bool:
        return asset_id in self._trusted

    def get_trusted(
        self,
    ) -> tuple[CodeAsset, ...]:
        assets: list[CodeAsset] = []

        for asset_id in sorted(self._trusted):
            asset = self.engine.get(asset_id)

            if asset is not None:
                assets.append(asset)

        return tuple(assets)

    def refresh(
        self,
        *,
        minimum_quality_score: float = 0.80,
        minimum_reliability_score: float = 0.80,
    ) -> tuple[CodeAssetTrustDecision, ...]:
        decisions: list[CodeAssetTrustDecision] = []

        for asset in self.engine.list_assets():
            decision = self.evaluate(
                asset.id,
                minimum_quality_score=minimum_quality_score,
                minimum_reliability_score=minimum_reliability_score,
            )

            if decision.trusted:
                self._trusted.add(asset.id)
            else:
                self._trusted.discard(asset.id)

            decisions.append(decision)

        return tuple(decisions)

    def clear(self) -> None:
        self._trusted.clear()

    @staticmethod
    def _validate_thresholds(
        minimum_quality_score: float,
        minimum_reliability_score: float,
    ) -> None:
        for name, value in (
            ("minimum_quality_score", minimum_quality_score),
            ("minimum_reliability_score", minimum_reliability_score),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0 and 1"
                )


trusted_templates = CodeLibraryTrustedTemplateRegistry()


__all__ = (
    "CodeAssetTrustDecision",
    "CodeLibraryTrustedTemplateRegistry",
    "trusted_templates",
)
