from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset
from .outcomes import CodeAssetOutcome, CodeAssetOutcomeType


@dataclass(frozen=True)
class CodeLibraryOutcomeContext:
    """Execution context carried across CL-9.2 outcome events."""

    build_id: str = ""
    project_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class CodeLibraryOutcomeRecorder:
    """Canonical CL-9.2 adapter for recording Code Library asset outcomes.

    This adapter deliberately sits at the Code Library boundary. It does not
    modify retrieval, composition, orchestration, validation, or testing
    implementations. Those subsystems can report their results through this
    contract when integration points are introduced.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def record(
        self,
        asset: CodeAsset,
        outcome: CodeAssetOutcomeType,
        *,
        success: bool | None = None,
        validation_passed: bool | None = None,
        testing_passed: bool | None = None,
        repair_count: int = 0,
        reuse_count: int = 1,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        context = context or CodeLibraryOutcomeContext()

        event = CodeAssetOutcome(
            asset_id=asset.id,
            outcome=outcome,
            success=success,
            validation_passed=validation_passed,
            testing_passed=testing_passed,
            repair_count=repair_count,
            reuse_count=reuse_count,
            build_id=context.build_id,
            project_id=context.project_id,
            metadata=dict(context.metadata),
        )

        return self.engine.record_outcome(event)

    def selected(
        self,
        asset: CodeAsset,
        *,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.SELECTED,
            context=context,
        )

    def composed(
        self,
        asset: CodeAsset,
        *,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.COMPOSED,
            context=context,
        )

    def executed(
        self,
        asset: CodeAsset,
        *,
        success: bool,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.EXECUTED,
            success=success,
            context=context,
        )

    def validated(
        self,
        asset: CodeAsset,
        *,
        passed: bool,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.VALIDATED,
            validation_passed=passed,
            context=context,
        )

    def tested(
        self,
        asset: CodeAsset,
        *,
        passed: bool,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.TESTED,
            testing_passed=passed,
            context=context,
        )

    def repaired(
        self,
        asset: CodeAsset,
        *,
        repair_count: int = 1,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.REPAIRED,
            repair_count=repair_count,
            context=context,
        )

    def succeeded(
        self,
        asset: CodeAsset,
        *,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.SUCCEEDED,
            success=True,
            context=context,
        )

    def failed(
        self,
        asset: CodeAsset,
        *,
        context: CodeLibraryOutcomeContext | None = None,
    ) -> CodeAsset:
        return self.record(
            asset,
            CodeAssetOutcomeType.FAILED,
            success=False,
            context=context,
        )

    def record_many(
        self,
        asset: CodeAsset,
        outcomes: Iterable[CodeAssetOutcome],
    ) -> CodeAsset:
        current = asset

        for outcome in outcomes:
            if outcome.asset_id != asset.id:
                raise ValueError(
                    "Outcome asset id does not match asset: "
                    f"{outcome.asset_id} != {asset.id}"
                )

            current = self.engine.record_outcome(outcome)

        return current


outcome_recorder = CodeLibraryOutcomeRecorder()


__all__ = (
    "CodeLibraryOutcomeContext",
    "CodeLibraryOutcomeRecorder",
    "outcome_recorder",
)
