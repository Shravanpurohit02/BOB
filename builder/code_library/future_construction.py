from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FutureConstructionAdjustment:
    asset_id: str
    score_delta: float
    confidence: float
    preferred: bool
    avoid: bool
    reasons: tuple[str, ...]
    metadata: dict

    def __post_init__(self):
        if not self.asset_id:
            raise ValueError("asset_id must not be empty")

        if not -10.0 <= self.score_delta <= 10.0:
            raise ValueError(
                "score_delta must be between -10.0 and 10.0"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "score_delta": self.score_delta,
            "confidence": self.confidence,
            "preferred": self.preferred,
            "avoid": self.avoid,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class FutureConstructionResult:
    adjustments: tuple[FutureConstructionAdjustment, ...]
    improved: bool
    preferred_assets: tuple[str, ...]
    avoided_assets: tuple[str, ...]
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "adjustments": [
                adjustment.to_dict()
                for adjustment in self.adjustments
            ],
            "improved": self.improved,
            "preferred_assets": list(
                self.preferred_assets
            ),
            "avoided_assets": list(
                self.avoided_assets
            ),
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryFutureConstruction:
    """
    Converts accumulated Knowledge Library / Code Library outcome
    records into deterministic adjustments for future construction.

    The component is deliberately policy-oriented rather than
    destructive: it does not delete assets or mutate the library.
    It produces selection/planning signals for subsequent builds.
    """

    def _adjustment_from_record(
        self,
        record,
    ) -> FutureConstructionAdjustment:
        if record.reusable:
            return FutureConstructionAdjustment(
                asset_id=record.asset_id,
                score_delta=min(
                    10.0,
                    max(
                        0.0,
                        record.score,
                    ),
                ),
                confidence=min(
                    1.0,
                    max(
                        0.0,
                        record.score / 10.0,
                    ),
                ),
                preferred=True,
                avoid=False,
                reasons=(
                    "previously_reusable",
                    "positive_outcome",
                ),
                metadata={
                    "record_id": record.record_id,
                    "outcome": record.outcome,
                },
            )

        return FutureConstructionAdjustment(
            asset_id=record.asset_id,
            score_delta=-min(
                10.0,
                max(
                    0.0,
                    10.0 - record.score,
                ),
            ),
            confidence=min(
                1.0,
                max(
                    0.0,
                    (10.0 - record.score) / 10.0,
                ),
            ),
            preferred=False,
            avoid=True,
            reasons=(
                "previously_failed",
                "negative_outcome",
            ),
            metadata={
                "record_id": record.record_id,
                "outcome": record.outcome,
            },
        )

    def improve(
        self,
        knowledge,
    ) -> FutureConstructionResult:
        if knowledge is None:
            raise TypeError(
                "knowledge must not be None"
            )

        if not hasattr(knowledge, "records"):
            raise TypeError(
                "knowledge must expose records"
            )

        adjustments_by_asset = {}

        for record in knowledge.records:
            adjustment = self._adjustment_from_record(
                record
            )

            existing = adjustments_by_asset.get(
                record.asset_id
            )

            if existing is None:
                adjustments_by_asset[
                    record.asset_id
                ] = adjustment
                continue

            # Keep the strongest accumulated signal for
            # deterministic future construction decisions.
            if (
                abs(adjustment.score_delta)
                > abs(existing.score_delta)
            ):
                adjustments_by_asset[
                    record.asset_id
                ] = adjustment

        adjustments = tuple(
            sorted(
                adjustments_by_asset.values(),
                key=lambda item: item.asset_id,
            )
        )

        preferred = tuple(
            adjustment.asset_id
            for adjustment in adjustments
            if adjustment.preferred
        )

        avoided = tuple(
            adjustment.asset_id
            for adjustment in adjustments
            if adjustment.avoid
        )

        if not adjustments:
            return FutureConstructionResult(
                adjustments=(),
                improved=False,
                preferred_assets=(),
                avoided_assets=(),
                score=0.0,
                reasons=(
                    "no_knowledge_records",
                    "future_construction_unchanged",
                ),
                metadata={
                    "record_count": 0,
                    "adjustment_count": 0,
                },
            )

        average_confidence = (
            sum(
                adjustment.confidence
                for adjustment in adjustments
            )
            / len(adjustments)
        )

        improvement_score = (
            10.0 * average_confidence
        )

        return FutureConstructionResult(
            adjustments=adjustments,
            improved=True,
            preferred_assets=preferred,
            avoided_assets=avoided,
            score=improvement_score,
            reasons=(
                "knowledge_records_received",
                "future_construction_adjustments_generated",
                "future_selection_improved",
            ),
            metadata={
                "record_count": len(
                    knowledge.records
                ),
                "adjustment_count": len(
                    adjustments
                ),
                "preferred_count": len(
                    preferred
                ),
                "avoided_count": len(
                    avoided
                ),
            },
        )

    def improve_future_construction(
        self,
        knowledge,
    ) -> FutureConstructionResult:
        return self.improve(knowledge)

    def apply_learning(
        self,
        knowledge,
    ) -> FutureConstructionResult:
        return self.improve(knowledge)


__all__ = [
    "FutureConstructionAdjustment",
    "FutureConstructionResult",
    "CodeLibraryFutureConstruction",
]
