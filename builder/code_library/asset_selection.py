from __future__ import annotations

from dataclasses import dataclass

from .retrieval_integration import (
    RequirementRetrievalResult,
)


@dataclass(frozen=True)
class AssetSelectionResult:
    requirement_name: str
    selected_assets: tuple
    rejected_assets: tuple
    best_asset: object | None
    score: float
    compatible: bool
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        def serialize(value):
            if hasattr(value, "to_dict"):
                return value.to_dict()
            return value

        return {
            "requirement_name": self.requirement_name,
            "selected_assets": [
                serialize(value)
                for value in self.selected_assets
            ],
            "rejected_assets": [
                serialize(value)
                for value in self.rejected_assets
            ],
            "best_asset": (
                serialize(self.best_asset)
                if self.best_asset is not None
                else None
            ),
            "score": self.score,
            "compatible": self.compatible,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryAssetSelector:
    """
    Selects reusable Code Library assets from the ranked CL-15.2
    retrieval result.

    Selection is deterministic. Candidates are considered in the
    retrieval engine's established order, while incompatible or
    invalid candidates are excluded without mutating the source
    retrieval result.
    """

    def select(
        self,
        result: RequirementRetrievalResult,
        *,
        limit: int | None = None,
    ) -> AssetSelectionResult:
        if not isinstance(
            result,
            RequirementRetrievalResult,
        ):
            raise TypeError(
                "result must be RequirementRetrievalResult"
            )

        if limit is not None:
            if not isinstance(limit, int):
                raise TypeError(
                    "limit must be an integer or None"
                )

            if limit < 0:
                raise ValueError(
                    "limit must be >= 0"
                )

        candidates = tuple(
            result.candidates
        )

        selected: list = []
        rejected: list = []

        for candidate in candidates:
            if not self._is_compatible(candidate):
                rejected.append(candidate)
                continue

            selected.append(candidate)

            if (
                limit is not None
                and len(selected) >= limit
            ):
                break

        best = (
            selected[0]
            if selected
            else None
        )

        reasons: list[str] = [
            "retrieval_candidates_received",
        ]

        if selected:
            reasons.append(
                "compatible_assets_selected"
            )
            reasons.append(
                "best_asset_selected"
            )
        else:
            reasons.append(
                "no_compatible_assets_selected"
            )

        if rejected:
            reasons.append(
                "incompatible_assets_rejected"
            )

        score = (
            float(
                getattr(
                    best,
                    "score",
                    result.score,
                )
            )
            if best is not None
            else 0.0
        )

        compatible = bool(selected)

        return AssetSelectionResult(
            requirement_name=result.requirement_name,
            selected_assets=tuple(selected),
            rejected_assets=tuple(rejected),
            best_asset=best,
            score=score,
            compatible=compatible,
            reasons=tuple(reasons),
            metadata={
                "candidate_count": len(candidates),
                "selected_count": len(selected),
                "rejected_count": len(rejected),
                "requested_limit": limit,
            },
        )

    @staticmethod
    def _is_compatible(candidate) -> bool:
        if candidate is None:
            return False

        if hasattr(candidate, "compatible"):
            return bool(
                candidate.compatible
            )

        if hasattr(candidate, "score"):
            return float(
                candidate.score
            ) > 0.0

        return True

    def select_best(
        self,
        result: RequirementRetrievalResult,
    ):
        selection = self.select(
            result,
            limit=1,
        )

        return selection.best_asset

    def select_from_retrieval(
        self,
        result: RequirementRetrievalResult,
        *,
        limit: int | None = None,
    ) -> AssetSelectionResult:
        return self.select(
            result,
            limit=limit,
        )


__all__ = [
    "AssetSelectionResult",
    "CodeLibraryAssetSelector",
]
