from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CodeAssetOutcomeType(str, Enum):
    """Canonical outcome categories for Code Library asset usage."""

    SELECTED = "selected"
    COMPOSED = "composed"
    EXECUTED = "executed"
    VALIDATED = "validated"
    TESTED = "tested"
    REPAIRED = "repaired"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class CodeAssetOutcome:
    """Canonical immutable record of an asset's participation in construction.

    The outcome contract deliberately separates asset participation from the
    final construction result. An asset may be selected or composed without
    the resulting project succeeding.
    """

    asset_id: str
    outcome: CodeAssetOutcomeType
    success: bool | None = None
    validation_passed: bool | None = None
    testing_passed: bool | None = None
    repair_count: int = 0
    reuse_count: int = 1
    build_id: str = ""
    project_id: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id is required")

        if self.repair_count < 0:
            raise ValueError("repair_count cannot be negative")

        if self.reuse_count < 1:
            raise ValueError("reuse_count must be at least 1")

        if self.timestamp < 0:
            raise ValueError("timestamp cannot be negative")

    @property
    def is_success(self) -> bool:
        return self.success is True

    @property
    def is_failure(self) -> bool:
        return self.success is False

    @property
    def required_repair(self) -> bool:
        return self.repair_count > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "outcome": self.outcome.value,
            "success": self.success,
            "validation_passed": self.validation_passed,
            "testing_passed": self.testing_passed,
            "repair_count": self.repair_count,
            "reuse_count": self.reuse_count,
            "build_id": self.build_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodeAssetOutcome":
        return cls(
            asset_id=str(data["asset_id"]),
            outcome=CodeAssetOutcomeType(data["outcome"]),
            success=data.get("success"),
            validation_passed=data.get("validation_passed"),
            testing_passed=data.get("testing_passed"),
            repair_count=int(data.get("repair_count", 0)),
            reuse_count=int(data.get("reuse_count", 1)),
            build_id=str(data.get("build_id", "")),
            project_id=str(data.get("project_id", "")),
            timestamp=float(data.get("timestamp", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class CodeAssetOutcomeSummary:
    """Aggregate performance projection for a Code Library asset."""

    asset_id: str
    uses: int = 0
    successes: int = 0
    failures: int = 0
    repairs: int = 0
    reuses: int = 0
    validation_passes: int = 0
    validation_failures: int = 0
    test_passes: int = 0
    test_failures: int = 0

    @property
    def success_rate(self) -> float:
        if self.uses <= 0:
            return 0.0
        return self.successes / self.uses

    @property
    def repair_rate(self) -> float:
        if self.uses <= 0:
            return 0.0
        return self.repairs / self.uses

    @property
    def reuse_rate(self) -> float:
        if self.uses <= 0:
            return 0.0
        return self.reuses / self.uses

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "uses": self.uses,
            "successes": self.successes,
            "failures": self.failures,
            "repairs": self.repairs,
            "reuses": self.reuses,
            "validation_passes": self.validation_passes,
            "validation_failures": self.validation_failures,
            "test_passes": self.test_passes,
            "test_failures": self.test_failures,
            "success_rate": self.success_rate,
            "repair_rate": self.repair_rate,
            "reuse_rate": self.reuse_rate,
        }
