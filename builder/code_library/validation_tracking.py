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
class CodeAssetValidationEvent:
    """Immutable CL-9.7 record of an asset validation result."""

    asset_id: str
    build_id: str
    passed: bool
    project_id: str = ""
    timestamp: float = 0.0
    validator: str = ""
    validation_stage: str = ""
    error_count: int = 0
    warning_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id is required")

        if not self.build_id:
            raise ValueError("build_id is required")

        if self.error_count < 0:
            raise ValueError("error_count cannot be negative")

        if self.warning_count < 0:
            raise ValueError("warning_count cannot be negative")

        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")

    @property
    def effective_timestamp(self) -> float:
        return self.timestamp if self.timestamp > 0 else _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "build_id": self.build_id,
            "passed": self.passed,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "validator": self.validator,
            "validation_stage": self.validation_stage,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CodeAssetValidationEvent":
        return cls(
            asset_id=str(data["asset_id"]),
            build_id=str(data["build_id"]),
            passed=bool(data["passed"]),
            project_id=str(data.get("project_id", "")),
            timestamp=float(data.get("timestamp", 0.0)),
            validator=str(data.get("validator", "")),
            validation_stage=str(
                data.get("validation_stage", "")
            ),
            error_count=int(data.get("error_count", 0)),
            warning_count=int(data.get("warning_count", 0)),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class CodeAssetValidationSummary:
    """Projection of validation results for one asset."""

    asset_id: str
    validations: int = 0
    passes: int = 0
    failures: int = 0
    errors: int = 0
    warnings: int = 0
    builds: int = 0
    projects: int = 0
    first_validation_at: float = 0.0
    last_validation_at: float = 0.0

    @property
    def pass_rate(self) -> float:
        if self.validations <= 0:
            return 0.0
        return self.passes / self.validations

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "validations": self.validations,
            "passes": self.passes,
            "failures": self.failures,
            "errors": self.errors,
            "warnings": self.warnings,
            "builds": self.builds,
            "projects": self.projects,
            "first_validation_at": self.first_validation_at,
            "last_validation_at": self.last_validation_at,
            "pass_rate": self.pass_rate,
        }


class CodeLibraryValidationTracker:
    """CL-9.7 tracker for validation results."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        recorder: CodeLibraryOutcomeRecorder | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.recorder = recorder or CodeLibraryOutcomeRecorder(self.engine)
        self._records: list[CodeAssetValidationEvent] = []

    def record(
        self,
        asset: CodeAsset,
        *,
        build_id: str,
        passed: bool,
        project_id: str = "",
        validator: str = "",
        validation_stage: str = "",
        error_count: int = 0,
        warning_count: int = 0,
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> CodeAssetValidationEvent:
        if self.engine.get(asset.id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset.id}"
            )

        event = CodeAssetValidationEvent(
            asset_id=asset.id,
            build_id=build_id,
            passed=passed,
            project_id=project_id,
            timestamp=timestamp,
            validator=validator,
            validation_stage=validation_stage,
            error_count=error_count,
            warning_count=warning_count,
            metadata=dict(metadata or {}),
        )

        self._records.append(event)

        self.recorder.validated(
            asset,
            passed=passed,
            context=CodeLibraryOutcomeContext(
                build_id=build_id,
                project_id=project_id,
                metadata={
                    "source": "cl-9.7-validation-tracker",
                    "validator": validator,
                    "validation_stage": validation_stage,
                    "error_count": error_count,
                    "warning_count": warning_count,
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
        passed: bool,
        project_id: str = "",
        validator: str = "",
        validation_stage: str = "",
        error_count: int = 0,
        warning_count: int = 0,
        timestamp: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[CodeAssetValidationEvent, ...]:
        return tuple(
            self.record(
                asset,
                build_id=build_id,
                passed=passed,
                project_id=project_id,
                validator=validator,
                validation_stage=validation_stage,
                error_count=error_count,
                warning_count=warning_count,
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
    ) -> tuple[CodeAssetValidationEvent, ...]:
        result: Iterable[CodeAssetValidationEvent] = self._records

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
    ) -> CodeAssetValidationSummary:
        if self.engine.get(asset_id) is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        records = self.records(
            asset_id,
            project_id=project_id,
        )

        summary = CodeAssetValidationSummary(
            asset_id=asset_id,
        )

        builds: set[str] = set()
        projects: set[str] = set()

        for record in records:
            summary.validations += 1

            if record.passed:
                summary.passes += 1
            else:
                summary.failures += 1

            summary.errors += record.error_count
            summary.warnings += record.warning_count

            if record.build_id:
                builds.add(record.build_id)

            if record.project_id:
                projects.add(record.project_id)

            timestamp = record.effective_timestamp

            if (
                summary.first_validation_at == 0.0
                or timestamp < summary.first_validation_at
            ):
                summary.first_validation_at = timestamp

            if timestamp > summary.last_validation_at:
                summary.last_validation_at = timestamp

        summary.builds = len(builds)
        summary.projects = len(projects)

        return summary

    def clear(self) -> None:
        self._records.clear()


validation_tracker = CodeLibraryValidationTracker()


__all__ = (
    "CodeAssetValidationEvent",
    "CodeAssetValidationSummary",
    "CodeLibraryValidationTracker",
    "validation_tracker",
)
