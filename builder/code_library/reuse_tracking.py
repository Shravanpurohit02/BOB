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
class CodeAssetReuseEvent:
    """Immutable CL-9.8 record of asset reuse during construction."""

    asset_id: str
    build_id: str
    reuse_count: int = 1
    project_id: str = ""
    timestamp: float = 0.0
    reuse_stage: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id is required")

        if not self.build_id:
            raise ValueError("build_id is required")

        if self.reuse_count < 1:
            raise ValueError("reuse_count must be at least 1")

        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")

    @property
    def effective_timestamp(self) -> float:
        return self.timestamp if self.timestamp > 0 else _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "build_id": self.build_id,
            "reuse_count": self.reuse_count,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "reuse_stage": self.reuse_stage,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CodeAssetReuseEvent":
        return cls(
            asset_id=str(data["asset_id"]),
            build_id=str(data["build_id"]),
            reuse_count=int(data.get("reuse_count", 1)),
            project_id=str(data.get("project_id", "")),
            timestamp=float(data.get("timestamp", 0.0)),
            reuse_stage=str(data.get("reuse_stage", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class CodeAssetReuseSummary:
    """Projection of reuse frequency for one asset."""

    asset_id: str
    reuse_events: int = 0
    total_reuses: int = 0
    builds: int = 0
    projects: int = 0
    first_reused_at: float = 0.0
    last_reused_at: float = 0.0

    @property
    def average_reuses_per_build(self) -> float:
        if self.builds <= 0:
            return 0.0
        return self.total_reuses / self.builds

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "reuse_events": self.reuse_events,
            "total_reuses": self.total_reuses,
            "builds": self.builds,
            "projects": self.projects,
            "first_reused_at": self.first_reused_at,
            "last_reused_at": self.last_reused_at,
            "average_reuses_per_build":
                self.average_reuses_per_build,
        }


class CodeLibraryReuseTracker:
    """CL-9.8 tracker for Code Library asset reuse frequency."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        recorder: CodeLibraryOutcomeRecorder | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.recorder = recorder or CodeLibraryOutcomeRecorder(self.engine)
        self._records: list[CodeAssetReuseEvent] = []

    def record(
        self,
        asset: CodeAsset,
        *,
        build_id: str,
        reuse_count: int = 1,
        project_id: str = "",
        reuse_stage: str = "",
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetReuseEvent:
        if self.engine.get(asset.id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset.id}"
            )

        event = CodeAssetReuseEvent(
            asset_id=asset.id,
            build_id=build_id,
            reuse_count=reuse_count,
            project_id=project_id,
            timestamp=timestamp,
            reuse_stage=reuse_stage,
            metadata=dict(metadata or {}),
        )

        self._records.append(event)

        self.recorder.record(
            asset,
            outcome=self._reuse_outcome_type(),
            reuse_count=reuse_count,
            context=CodeLibraryOutcomeContext(
                build_id=build_id,
                project_id=project_id,
                metadata={
                    "source": "cl-9.8-reuse-tracker",
                    "reuse_stage": reuse_stage,
                    **dict(metadata or {}),
                },
            ),
        )

        return event

    def record_many(
        self,
        assets: Iterable[CodeAsset],
        *,
        build_id: str,
        reuse_count: int = 1,
        project_id: str = "",
        reuse_stage: str = "",
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[CodeAssetReuseEvent, ...]:
        return tuple(
            self.record(
                asset,
                build_id=build_id,
                reuse_count=reuse_count,
                project_id=project_id,
                reuse_stage=reuse_stage,
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
    ) -> tuple[CodeAssetReuseEvent, ...]:
        result: Iterable[CodeAssetReuseEvent] = self._records

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
    ) -> CodeAssetReuseSummary:
        if self.engine.get(asset_id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        records = self.records(
            asset_id,
            project_id=project_id,
        )

        summary = CodeAssetReuseSummary(
            asset_id=asset_id,
        )

        builds: set[str] = set()
        projects: set[str] = set()

        for record in records:
            summary.reuse_events += 1
            summary.total_reuses += record.reuse_count

            if record.build_id:
                builds.add(record.build_id)

            if record.project_id:
                projects.add(record.project_id)

            timestamp = record.effective_timestamp

            if (
                summary.first_reused_at == 0.0
                or timestamp < summary.first_reused_at
            ):
                summary.first_reused_at = timestamp

            if timestamp > summary.last_reused_at:
                summary.last_reused_at = timestamp

        summary.builds = len(builds)
        summary.projects = len(projects)

        return summary

    def clear(self) -> None:
        self._records.clear()

    @staticmethod
    def _reuse_outcome_type():
        from .outcomes import CodeAssetOutcomeType
        return CodeAssetOutcomeType.COMPOSED


reuse_tracker = CodeLibraryReuseTracker()


__all__ = (
    "CodeAssetReuseEvent",
    "CodeAssetReuseSummary",
    "CodeLibraryReuseTracker",
    "reuse_tracker",
)
