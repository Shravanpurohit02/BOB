from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .engine import CodeLibraryEngine
from .success_rates import (
    CodeAssetSuccessRate,
    CodeLibrarySuccessRateCalculator,
)


@dataclass(frozen=True)
class CodeAssetSuccessProfile:
    """CL-9.10 deterministic profile for consistent asset success."""

    asset_id: str
    successful_builds: int
    failed_builds: int
    total_builds: int
    success_rate: float
    minimum_builds: int
    minimum_success_rate: float
    consistently_successful: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "successful_builds": self.successful_builds,
            "failed_builds": self.failed_builds,
            "total_builds": self.total_builds,
            "success_rate": self.success_rate,
            "minimum_builds": self.minimum_builds,
            "minimum_success_rate": self.minimum_success_rate,
            "consistently_successful": self.consistently_successful,
        }


class CodeLibrarySuccessDetector:
    """Detect assets with consistently successful build outcomes.

    Detection is intentionally analytical only. CL-9.10 does not promote,
    demote, rank, or modify assets. Those decisions belong to CL-10.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        calculator: CodeLibrarySuccessRateCalculator | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.calculator = (
            calculator
            or CodeLibrarySuccessRateCalculator(self.engine)
        )

    def detect(
        self,
        asset_id: str,
        *,
        minimum_builds: int = 3,
        minimum_success_rate: float = 1.0,
    ) -> CodeAssetSuccessProfile:
        self._validate_thresholds(
            minimum_builds,
            minimum_success_rate,
        )

        if self.engine.get(asset_id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        result = self.calculator.calculate(asset_id)

        return self._profile(
            result,
            minimum_builds=minimum_builds,
            minimum_success_rate=minimum_success_rate,
        )

    def detect_many(
        self,
        asset_ids: Iterable[str],
        *,
        minimum_builds: int = 3,
        minimum_success_rate: float = 1.0,
    ) -> tuple[CodeAssetSuccessProfile, ...]:
        self._validate_thresholds(
            minimum_builds,
            minimum_success_rate,
        )

        return tuple(
            self.detect(
                asset_id,
                minimum_builds=minimum_builds,
                minimum_success_rate=minimum_success_rate,
            )
            for asset_id in asset_ids
        )

    def detect_all(
        self,
        *,
        minimum_builds: int = 3,
        minimum_success_rate: float = 1.0,
    ) -> tuple[CodeAssetSuccessProfile, ...]:
        return self.detect_many(
            (
                asset.id
                for asset in self.engine.list_assets()
            ),
            minimum_builds=minimum_builds,
            minimum_success_rate=minimum_success_rate,
        )

    def consistently_successful(
        self,
        asset_id: str,
        *,
        minimum_builds: int = 3,
        minimum_success_rate: float = 1.0,
    ) -> bool:
        return self.detect(
            asset_id,
            minimum_builds=minimum_builds,
            minimum_success_rate=minimum_success_rate,
        ).consistently_successful

    @staticmethod
    def _profile(
        result: CodeAssetSuccessRate,
        *,
        minimum_builds: int,
        minimum_success_rate: float,
    ) -> CodeAssetSuccessProfile:
        consistent = (
            result.total_builds >= minimum_builds
            and result.success_rate >= minimum_success_rate
        )

        return CodeAssetSuccessProfile(
            asset_id=result.asset_id,
            successful_builds=result.successful_builds,
            failed_builds=result.failed_builds,
            total_builds=result.total_builds,
            success_rate=result.success_rate,
            minimum_builds=minimum_builds,
            minimum_success_rate=minimum_success_rate,
            consistently_successful=consistent,
        )

    @staticmethod
    def _validate_thresholds(
        minimum_builds: int,
        minimum_success_rate: float,
    ) -> None:
        if minimum_builds < 1:
            raise ValueError(
                "minimum_builds must be at least 1"
            )

        if not 0.0 <= minimum_success_rate <= 1.0:
            raise ValueError(
                "minimum_success_rate must be between 0 and 1"
            )


success_detector = CodeLibrarySuccessDetector()


__all__ = (
    "CodeAssetSuccessProfile",
    "CodeLibrarySuccessDetector",
    "success_detector",
)
