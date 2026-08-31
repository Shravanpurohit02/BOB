from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset
from .outcomes import (
    CodeAssetOutcome,
    CodeAssetOutcomeSummary,
    CodeAssetOutcomeType,
)
from .build_outcomes import CodeLibrarySuccessfulBuildTracker
from .build_failures import CodeLibraryFailedBuildTracker


@dataclass(frozen=True)
class CodeAssetSuccessRate:
    """Deterministic CL-9.9 success-rate projection for one asset."""

    asset_id: str
    successful_builds: int = 0
    failed_builds: int = 0
    total_builds: int = 0
    success_rate: float = 0.0

    @property
    def failure_rate(self) -> float:
        if self.total_builds <= 0:
            return 0.0
        return self.failed_builds / self.total_builds

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "successful_builds": self.successful_builds,
            "failed_builds": self.failed_builds,
            "total_builds": self.total_builds,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
        }


class CodeLibrarySuccessRateCalculator:
    """CL-9.9 calculator for asset construction success rates.

    Success rate is calculated from distinct successful and failed build
    participation. A build is counted once per asset regardless of repeated
    notifications or multiple construction events.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        successful_builds: CodeLibrarySuccessfulBuildTracker | None = None,
        failed_builds: CodeLibraryFailedBuildTracker | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.successful_builds = (
            successful_builds
            or CodeLibrarySuccessfulBuildTracker(self.engine)
        )
        self.failed_builds = (
            failed_builds
            or CodeLibraryFailedBuildTracker(self.engine)
        )

    def calculate(
        self,
        asset_id: str,
    ) -> CodeAssetSuccessRate:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        successful = {
            record.build_id
            for record in self.successful_builds.records(asset_id)
        }

        failed = {
            record.build_id
            for record in self.failed_builds.records(asset_id)
        }

        total = successful | failed

        successful_count = len(successful)
        failed_count = len(failed)
        total_count = len(total)

        rate = (
            successful_count / total_count
            if total_count > 0
            else 0.0
        )

        return CodeAssetSuccessRate(
            asset_id=asset_id,
            successful_builds=successful_count,
            failed_builds=failed_count,
            total_builds=total_count,
            success_rate=rate,
        )

    def calculate_many(
        self,
        asset_ids: Iterable[str],
    ) -> tuple[CodeAssetSuccessRate, ...]:
        return tuple(
            self.calculate(asset_id)
            for asset_id in asset_ids
        )

    def calculate_all(self) -> tuple[CodeAssetSuccessRate, ...]:
        return self.calculate_many(
            asset.id
            for asset in self.engine.list_assets()
        )

    @staticmethod
    def from_outcomes(
        asset_id: str,
        outcomes: Iterable[CodeAssetOutcome],
    ) -> CodeAssetSuccessRate:
        successful: set[str] = set()
        failed: set[str] = set()

        for outcome in outcomes:
            if outcome.asset_id != asset_id:
                raise ValueError(
                    "Outcome asset id does not match requested asset: "
                    f"{outcome.asset_id} != {asset_id}"
                )

            if not outcome.build_id:
                continue

            if outcome.outcome is CodeAssetOutcomeType.SUCCEEDED:
                successful.add(outcome.build_id)

            elif outcome.outcome is CodeAssetOutcomeType.FAILED:
                failed.add(outcome.build_id)

        total = successful | failed

        successful_count = len(successful)
        failed_count = len(failed)
        total_count = len(total)

        return CodeAssetSuccessRate(
            asset_id=asset_id,
            successful_builds=successful_count,
            failed_builds=failed_count,
            total_builds=total_count,
            success_rate=(
                successful_count / total_count
                if total_count > 0
                else 0.0
            ),
        )


success_rate_calculator = CodeLibrarySuccessRateCalculator()


__all__ = (
    "CodeAssetSuccessRate",
    "CodeLibrarySuccessRateCalculator",
    "success_rate_calculator",
)
