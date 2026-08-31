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
class CodeAssetRepairEvent:
    """Immutable CL-9.6 record of asset repair during construction."""

    asset_id: str
    build_id: str
    repair_count: int = 1
    project_id: str = ""
    timestamp: float = 0.0
    repair_reason: str = ""
    repair_stage: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id is required")

        if not self.build_id:
            raise ValueError("build_id is required")

        if self.repair_count < 1:
            raise ValueError("repair_count must be at least 1")

        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")

    @property
    def effective_timestamp(self) -> float:
        return self.timestamp if self.timestamp > 0 else _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "build_id": self.build_id,
            "repair_count": self.repair_count,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "repair_reason": self.repair_reason,
            "repair_stage": self.repair_stage,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CodeAssetRepairEvent":
        return cls(
            asset_id=str(data["asset_id"]),
            build_id=str(data["build_id"]),
            repair_count=int(data.get("repair_count", 1)),
            project_id=str(data.get("project_id", "")),
            timestamp=float(data.get("timestamp", 0.0)),
            repair_reason=str(data.get("repair_reason", "")),
            repair_stage=str(data.get("repair_stage", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class CodeAssetRepairSummary:
    """Projection of repair frequency for one asset."""

    asset_id: str
    repair_events: int = 0
    total_repairs: int = 0
    repaired_builds: int = 0
    projects: int = 0
    first_repair_at: float = 0.0
    last_repair_at: float = 0.0

    @property
    def average_repairs_per_repaired_build(self) -> float:
        if self.repaired_builds <= 0:
            return 0.0
        return self.total_repairs / self.repaired_builds

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "repair_events": self.repair_events,
            "total_repairs": self.total_repairs,
            "repaired_builds": self.repaired_builds,
            "projects": self.projects,
            "first_repair_at": self.first_repair_at,
            "last_repair_at": self.last_repair_at,
            "average_repairs_per_repaired_build":
                self.average_repairs_per_repaired_build,
        }


class CodeLibraryRepairTracker:
    """CL-9.6 tracker for construction repair frequency."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        recorder: CodeLibraryOutcomeRecorder | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.recorder = recorder or CodeLibraryOutcomeRecorder(self.engine)
        self._records: list[CodeAssetRepairEvent] = []

    def record(
        self,
        asset: CodeAsset,
        *,
        build_id: str,
        repair_count: int = 1,
        project_id: str = "",
        repair_reason: str = "",
        repair_stage: str = "",
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetRepairEvent:
        if self.engine.get(asset.id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset.id}"
            )

        candidate = CodeAssetRepairEvent(
            asset_id=asset.id,
            build_id=build_id,
            repair_count=repair_count,
            project_id=project_id,
            timestamp=timestamp,
            repair_reason=repair_reason,
            repair_stage=repair_stage,
            metadata=dict(metadata or {}),
        )

        self._records.append(candidate)

        self.recorder.repaired(
            asset,
            repair_count=repair_count,
            context=CodeLibraryOutcomeContext(
                build_id=build_id,
                project_id=project_id,
                metadata={
                    "source": "cl-9.6-repair-tracker",
                    "repair_reason": repair_reason,
                    "repair_stage": repair_stage,
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
        repair_count: int = 1,
        project_id: str = "",
        repair_reason: str = "",
        repair_stage: str = "",
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[CodeAssetRepairEvent, ...]:
        return tuple(
            self.record(
                asset,
                build_id=build_id,
                repair_count=repair_count,
                project_id=project_id,
                repair_reason=repair_reason,
                repair_stage=repair_stage,
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
    ) -> tuple[CodeAssetRepairEvent, ...]:
        result: Iterable[CodeAssetRepairEvent] = self._records

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
    ) -> CodeAssetRepairSummary:
        if self.engine.get(asset_id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        records = self.records(
            asset_id,
            project_id=project_id,
        )

        summary = CodeAssetRepairSummary(
            asset_id=asset_id,
        )

        repaired_build_ids: set[str] = set()
        projects: set[str] = set()

        for record in records:
            summary.repair_events += 1
            summary.total_repairs += record.repair_count
            repaired_build_ids.add(record.build_id)

            if record.project_id:
                projects.add(record.project_id)

            timestamp = record.effective_timestamp

            if (
                summary.first_repair_at == 0.0
                or timestamp < summary.first_repair_at
            ):
                summary.first_repair_at = timestamp

            if timestamp > summary.last_repair_at:
                summary.last_repair_at = timestamp

        summary.repaired_builds = len(repaired_build_ids)
        summary.projects = len(projects)

        return summary

    def clear(self) -> None:
        self._records.clear()


repair_tracker = CodeLibraryRepairTracker()


__all__ = (
    "CodeAssetRepairEvent",
    "CodeAssetRepairSummary",
    "CodeLibraryRepairTracker",
    "repair_tracker",
)
