from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset


def _now() -> float:
    return datetime.now(timezone.utc).timestamp()


class CodeAssetUsageStage(str, Enum):
    """Construction stages at which a Code Library asset can be used."""

    SELECTED = "selected"
    COMPOSED = "composed"
    INSTANTIATED = "instantiated"
    GENERATED = "generated"
    EXECUTED = "executed"


@dataclass(frozen=True)
class CodeAssetUsageEvent:
    """Immutable CL-9.3 record of one asset-use occurrence."""

    asset_id: str
    stage: CodeAssetUsageStage
    build_id: str = ""
    project_id: str = ""
    timestamp: float = 0.0
    quantity: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id is required")

        if self.quantity < 1:
            raise ValueError("quantity must be at least 1")

        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")

    @property
    def effective_timestamp(self) -> float:
        return self.timestamp if self.timestamp > 0 else _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "stage": self.stage.value,
            "build_id": self.build_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "quantity": self.quantity,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CodeAssetUsageEvent":
        return cls(
            asset_id=str(data["asset_id"]),
            stage=CodeAssetUsageStage(data["stage"]),
            build_id=str(data.get("build_id", "")),
            project_id=str(data.get("project_id", "")),
            timestamp=float(data.get("timestamp", 0.0)),
            quantity=int(data.get("quantity", 1)),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class CodeAssetUsageSummary:
    """Deterministic projection of construction usage for one asset."""

    asset_id: str
    total_uses: int = 0
    selected: int = 0
    composed: int = 0
    instantiated: int = 0
    generated: int = 0
    executed: int = 0
    builds: int = 0
    projects: int = 0
    first_used_at: float = 0.0
    last_used_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "total_uses": self.total_uses,
            "selected": self.selected,
            "composed": self.composed,
            "instantiated": self.instantiated,
            "generated": self.generated,
            "executed": self.executed,
            "builds": self.builds,
            "projects": self.projects,
            "first_used_at": self.first_used_at,
            "last_used_at": self.last_used_at,
        }


class CodeLibraryUsageTracker:
    """CL-9.3 construction usage tracker.

    Usage events are deliberately separate from the compact legacy
    CodeAssetUsage projection. This preserves CL-9.1/9.2 semantics while
    providing detailed construction-level usage information for later
    learning phases.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self._events: list[CodeAssetUsageEvent] = []

    def record(
        self,
        asset: CodeAsset,
        stage: CodeAssetUsageStage,
        *,
        build_id: str = "",
        project_id: str = "",
        quantity: int = 1,
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetUsageEvent:
        self.engine.get(asset.id) or self._require_registered(asset)

        event = CodeAssetUsageEvent(
            asset_id=asset.id,
            stage=stage,
            build_id=build_id,
            project_id=project_id,
            timestamp=timestamp,
            quantity=quantity,
            metadata=dict(metadata or {}),
        )

        self._events.append(event)

        return event

    def selected(
        self,
        asset: CodeAsset,
        *,
        build_id: str = "",
        project_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetUsageEvent:
        return self.record(
            asset,
            CodeAssetUsageStage.SELECTED,
            build_id=build_id,
            project_id=project_id,
            metadata=metadata,
        )

    def composed(
        self,
        asset: CodeAsset,
        *,
        build_id: str = "",
        project_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetUsageEvent:
        return self.record(
            asset,
            CodeAssetUsageStage.COMPOSED,
            build_id=build_id,
            project_id=project_id,
            metadata=metadata,
        )

    def instantiated(
        self,
        asset: CodeAsset,
        *,
        build_id: str = "",
        project_id: str = "",
        quantity: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetUsageEvent:
        return self.record(
            asset,
            CodeAssetUsageStage.INSTANTIATED,
            build_id=build_id,
            project_id=project_id,
            quantity=quantity,
            metadata=metadata,
        )

    def generated(
        self,
        asset: CodeAsset,
        *,
        build_id: str = "",
        project_id: str = "",
        quantity: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetUsageEvent:
        return self.record(
            asset,
            CodeAssetUsageStage.GENERATED,
            build_id=build_id,
            project_id=project_id,
            quantity=quantity,
            metadata=metadata,
        )

    def executed(
        self,
        asset: CodeAsset,
        *,
        build_id: str = "",
        project_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetUsageEvent:
        return self.record(
            asset,
            CodeAssetUsageStage.EXECUTED,
            build_id=build_id,
            project_id=project_id,
            metadata=metadata,
        )

    def events(
        self,
        asset_id: str | None = None,
        *,
        build_id: str | None = None,
        project_id: str | None = None,
    ) -> tuple[CodeAssetUsageEvent, ...]:
        result: Iterable[CodeAssetUsageEvent] = self._events

        if asset_id is not None:
            result = (
                event
                for event in result
                if event.asset_id == asset_id
            )

        if build_id is not None:
            result = (
                event
                for event in result
                if event.build_id == build_id
            )

        if project_id is not None:
            result = (
                event
                for event in result
                if event.project_id == project_id
            )

        return tuple(result)

    def summary(
        self,
        asset_id: str,
        *,
        build_id: str | None = None,
        project_id: str | None = None,
    ) -> CodeAssetUsageSummary:
        self.engine.get(asset_id) or self._require_asset(asset_id)

        events = self.events(
            asset_id,
            build_id=build_id,
            project_id=project_id,
        )

        summary = CodeAssetUsageSummary(
            asset_id=asset_id,
        )

        builds: set[str] = set()
        projects: set[str] = set()

        for event in events:
            quantity = event.quantity
            summary.total_uses += quantity

            if event.stage is CodeAssetUsageStage.SELECTED:
                summary.selected += quantity
            elif event.stage is CodeAssetUsageStage.COMPOSED:
                summary.composed += quantity
            elif event.stage is CodeAssetUsageStage.INSTANTIATED:
                summary.instantiated += quantity
            elif event.stage is CodeAssetUsageStage.GENERATED:
                summary.generated += quantity
            elif event.stage is CodeAssetUsageStage.EXECUTED:
                summary.executed += quantity

            if event.build_id:
                builds.add(event.build_id)

            if event.project_id:
                projects.add(event.project_id)

            timestamp = event.effective_timestamp

            if (
                summary.first_used_at == 0.0
                or timestamp < summary.first_used_at
            ):
                summary.first_used_at = timestamp

            if timestamp > summary.last_used_at:
                summary.last_used_at = timestamp

        summary.builds = len(builds)
        summary.projects = len(projects)

        return summary

    def clear(self) -> None:
        self._events.clear()

    def _require_asset(self, asset_id: str) -> CodeAsset:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        return asset

    def _require_registered(self, asset: CodeAsset) -> CodeAsset:
        raise KeyError(
            f"Code Library asset not found: {asset.id}"
        )


usage_tracker = CodeLibraryUsageTracker()


__all__ = (
    "CodeAssetUsageStage",
    "CodeAssetUsageEvent",
    "CodeAssetUsageSummary",
    "CodeLibraryUsageTracker",
    "usage_tracker",
)
