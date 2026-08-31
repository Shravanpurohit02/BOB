from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset
from .outcome_integration import (
    CodeLibraryOutcomeContext,
    CodeLibraryOutcomeRecorder,
)


def _now() -> float:
    return datetime.now(timezone.utc).timestamp()


@dataclass(frozen=True)
class CodeAssetBuildFailure:
    """Immutable CL-9.5 record of an asset participating in a failed build."""

    asset_id: str
    build_id: str
    project_id: str = ""
    timestamp: float = 0.0
    failure_reason: str = ""
    failure_stage: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id is required")

        if not self.build_id:
            raise ValueError("build_id is required")

        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")

    @property
    def effective_timestamp(self) -> float:
        return self.timestamp if self.timestamp > 0 else _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "build_id": self.build_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "failure_reason": self.failure_reason,
            "failure_stage": self.failure_stage,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CodeAssetBuildFailure":
        return cls(
            asset_id=str(data["asset_id"]),
            build_id=str(data["build_id"]),
            project_id=str(data.get("project_id", "")),
            timestamp=float(data.get("timestamp", 0.0)),
            failure_reason=str(data.get("failure_reason", "")),
            failure_stage=str(data.get("failure_stage", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class CodeAssetBuildFailureSummary:
    """Projection of failed-build participation for one asset."""

    asset_id: str
    failed_builds: int = 0
    projects: int = 0
    first_failure_at: float = 0.0
    last_failure_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "failed_builds": self.failed_builds,
            "projects": self.projects,
            "first_failure_at": self.first_failure_at,
            "last_failure_at": self.last_failure_at,
        }


class CodeLibraryFailedBuildTracker:
    """CL-9.5 tracker for failed construction outcomes.

    A failed build is counted once per asset/build pair. Repeated failure
    notifications for the same asset and build are idempotent.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        recorder: CodeLibraryOutcomeRecorder | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.recorder = recorder or CodeLibraryOutcomeRecorder(self.engine)
        self._records: list[CodeAssetBuildFailure] = []

    def record(
        self,
        asset: CodeAsset,
        *,
        build_id: str,
        project_id: str = "",
        failure_reason: str = "",
        failure_stage: str = "",
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetBuildFailure:
        if self.engine.get(asset.id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset.id}"
            )

        candidate = CodeAssetBuildFailure(
            asset_id=asset.id,
            build_id=build_id,
            project_id=project_id,
            timestamp=timestamp,
            failure_reason=failure_reason,
            failure_stage=failure_stage,
            metadata=dict(metadata or {}),
        )

        for existing in self._records:
            if (
                existing.asset_id == candidate.asset_id
                and existing.build_id == candidate.build_id
            ):
                return existing

        self._records.append(candidate)

        self.recorder.failed(
            asset,
            context=CodeLibraryOutcomeContext(
                build_id=build_id,
                project_id=project_id,
                metadata={
                    "source": "cl-9.5-failed-build-tracker",
                    "failure_reason": failure_reason,
                    "failure_stage": failure_stage,
                    **dict(metadata or {}),
                },
            ),
        )

        return candidate

    def record_many(
        self,
        assets: Iterable[CodeAsset],
        *,
        build_id: str,
        project_id: str = "",
        failure_reason: str = "",
        failure_stage: str = "",
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[CodeAssetBuildFailure, ...]:
        return tuple(
            self.record(
                asset,
                build_id=build_id,
                project_id=project_id,
                failure_reason=failure_reason,
                failure_stage=failure_stage,
                timestamp=timestamp,
                metadata=metadata,
            )
            for asset in assets
        )

    def records(
        self,
        asset_id: str | None = None,
        *,
        build_id: str | None = None,
        project_id: str | None = None,
    ) -> tuple[CodeAssetBuildFailure, ...]:
        result: Iterable[CodeAssetBuildFailure] = self._records

        if asset_id is not None:
            result = (
                record
                for record in result
                if record.asset_id == asset_id
            )

        if build_id is not None:
            result = (
                record
                for record in result
                if record.build_id == build_id
            )

        if project_id is not None:
            result = (
                record
                for record in result
                if record.project_id == project_id
            )

        return tuple(result)

    def summary(
        self,
        asset_id: str,
        *,
        project_id: str | None = None,
    ) -> CodeAssetBuildFailureSummary:
        if self.engine.get(asset_id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        records = self.records(
            asset_id,
            project_id=project_id,
        )

        summary = CodeAssetBuildFailureSummary(
            asset_id=asset_id,
        )

        projects: set[str] = set()

        for record in records:
            summary.failed_builds += 1

            if record.project_id:
                projects.add(record.project_id)

            timestamp = record.effective_timestamp

            if (
                summary.first_failure_at == 0.0
                or timestamp < summary.first_failure_at
            ):
                summary.first_failure_at = timestamp

            if timestamp > summary.last_failure_at:
                summary.last_failure_at = timestamp

        summary.projects = len(projects)

        return summary

    def clear(self) -> None:
        self._records.clear()


failed_build_tracker = CodeLibraryFailedBuildTracker()


__all__ = (
    "CodeAssetBuildFailure",
    "CodeAssetBuildFailureSummary",
    "CodeLibraryFailedBuildTracker",
    "failed_build_tracker",
)
