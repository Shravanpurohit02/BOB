from __future__ import annotations

from .lifecycle import CodeLibraryLifecycle
from .models import (
    CodeAsset,
    CodeAssetLifecycle,
    CodeAssetUsage,
)
from .outcomes import (
    CodeAssetOutcome,
    CodeAssetOutcomeSummary,
    CodeAssetOutcomeType,
)
from .provenance import CodeLibraryProvenance
from .store import CodeLibraryStore


class CodeLibraryEngine:
    """
    Foundation service for the BOB Code Library.

    CL-1 intentionally provides canonical asset persistence,
    provenance validation, lifecycle control and usage accounting.
    Retrieval and application composition are implemented in
    later Code Library phases.
    """

    def __init__(
        self,
        store: CodeLibraryStore | None = None,
    ) -> None:
        self.store = store or CodeLibraryStore()

    def register(
        self,
        asset: CodeAsset,
    ) -> CodeAsset:
        if not asset.id.strip():
            raise ValueError(
                "Code Library asset id is required"
            )

        if not asset.name.strip():
            raise ValueError(
                "Code Library asset name is required"
            )

        asset.id = asset.id.strip()

        existing = self.store.get(asset.id)

        if existing is not None:
            raise ValueError(
                f"Code Library asset already exists: {asset.id}"
            )

        self.store.save(asset)
        return asset

    def get(
        self,
        asset_id: str,
    ) -> CodeAsset | None:
        return self.store.get(asset_id)

    def validate(
        self,
        asset_id: str,
    ) -> CodeAsset:
        asset = self._require(asset_id)

        valid, issues = (
            CodeLibraryProvenance.validate_asset(
                asset
            )
        )

        if not valid:
            raise ValueError(
                "Code Library provenance validation failed: "
                + "; ".join(issues)
            )

        CodeLibraryLifecycle.validate(asset)
        return self.store.save(asset)

    def promote(
        self,
        asset_id: str,
    ) -> CodeAsset:
        asset = self._require(asset_id)

        CodeLibraryLifecycle.promote(asset)
        return self.store.save(asset)

    def deprecate(
        self,
        asset_id: str,
    ) -> CodeAsset:
        asset = self._require(asset_id)

        CodeLibraryLifecycle.deprecate(asset)
        return self.store.save(asset)

    def record_use(
        self,
        asset_id: str,
        *,
        success: bool,
    ) -> CodeAsset:
        """Record a legacy success/failure usage event.

        This compatibility API translates the simple usage signal into
        the canonical CL-9.1 outcome contract.
        """
        outcome = CodeAssetOutcome(
            asset_id=asset_id,
            outcome=(
                CodeAssetOutcomeType.SUCCEEDED
                if success
                else CodeAssetOutcomeType.FAILED
            ),
            success=success,
        )
        return self.record_outcome(outcome)

    def record_outcome(
        self,
        outcome: CodeAssetOutcome,
    ) -> CodeAsset:
        """Record a canonical CL-9.1 asset outcome.

        The existing CodeAssetUsage structure remains the compact
        persistent usage projection. CL-9.1 outcome semantics are
        translated into that projection without changing the
        canonical CodeAsset model.
        """
        asset = self._require(outcome.asset_id)

        usage: CodeAssetUsage = asset.usage

        if outcome.outcome in {
            CodeAssetOutcomeType.SELECTED,
            CodeAssetOutcomeType.COMPOSED,
            CodeAssetOutcomeType.EXECUTED,
            CodeAssetOutcomeType.SUCCEEDED,
            CodeAssetOutcomeType.FAILED,
        }:
            usage.uses += 1

        if outcome.outcome is CodeAssetOutcomeType.SUCCEEDED:
            usage.successes += 1
            if outcome.timestamp > 0:
                usage.last_success_at = str(
                    outcome.timestamp
                )

        elif outcome.outcome is CodeAssetOutcomeType.FAILED:
            usage.failures += 1
            if outcome.timestamp > 0:
                usage.last_failure_at = str(
                    outcome.timestamp
                )

        return self.store.save(asset)

    def outcome_summary(
        self,
        asset_id: str,
        outcomes: list[CodeAssetOutcome],
    ) -> CodeAssetOutcomeSummary:
        """Build a deterministic CL-9.1 outcome summary for an asset."""
        self._require(asset_id)

        summary = CodeAssetOutcomeSummary(
            asset_id=asset_id,
        )

        for outcome in outcomes:
            if outcome.asset_id != asset_id:
                raise ValueError(
                    "Outcome asset id does not match requested asset: "
                    f"{outcome.asset_id} != {asset_id}"
                )

            if outcome.outcome in {
                CodeAssetOutcomeType.SELECTED,
                CodeAssetOutcomeType.COMPOSED,
                CodeAssetOutcomeType.EXECUTED,
                CodeAssetOutcomeType.SUCCEEDED,
                CodeAssetOutcomeType.FAILED,
            }:
                summary.uses += 1

            if outcome.outcome is CodeAssetOutcomeType.SUCCEEDED:
                summary.successes += 1

            elif outcome.outcome is CodeAssetOutcomeType.FAILED:
                summary.failures += 1

            if outcome.repair_count > 0:
                summary.repairs += outcome.repair_count

            if outcome.reuse_count > 1:
                summary.reuses += outcome.reuse_count - 1

            if outcome.outcome is CodeAssetOutcomeType.VALIDATED:
                if outcome.validation_passed is True:
                    summary.validation_passes += 1
                elif outcome.validation_passed is False:
                    summary.validation_failures += 1

            if outcome.outcome is CodeAssetOutcomeType.TESTED:
                if outcome.testing_passed is True:
                    summary.test_passes += 1
                elif outcome.testing_passed is False:
                    summary.test_failures += 1

        return summary

    def list_assets(self) -> list[CodeAsset]:
        return self.store.all()

    def _require(
        self,
        asset_id: str,
    ) -> CodeAsset:
        asset = self.store.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        return asset


engine = CodeLibraryEngine()

__all__ = (
    "CodeLibraryEngine",
    "engine",
)
