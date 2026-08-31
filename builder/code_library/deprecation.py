from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAssetLifecycle


@dataclass(frozen=True)
class CodeAssetDeprecationDecision:
    """Deterministic CL-10.6 deprecation decision."""

    asset_id: str
    should_deprecate: bool
    lifecycle: str
    reason: str
    source: str = "code-library"

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "should_deprecate": self.should_deprecate,
            "lifecycle": self.lifecycle,
            "reason": self.reason,
            "source": self.source,
        }


class CodeLibraryDeprecationManager:
    """Explicit and deterministic asset deprecation management.

    CL-10.6 centralizes deprecation decisions and execution while preserving
    the existing Code Library lifecycle contract.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def evaluate(
        self,
        asset_id: str,
        *,
        reason: str,
        source: str = "code-library",
    ) -> CodeAssetDeprecationDecision:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        normalized_reason = str(reason).strip()

        if not normalized_reason:
            raise ValueError(
                "Deprecation reason is required"
            )

        if asset.lifecycle == CodeAssetLifecycle.DEPRECATED.value:
            return CodeAssetDeprecationDecision(
                asset_id=asset_id,
                should_deprecate=False,
                lifecycle=asset.lifecycle,
                reason=normalized_reason,
                source=source,
            )

        return CodeAssetDeprecationDecision(
            asset_id=asset_id,
            should_deprecate=True,
            lifecycle=asset.lifecycle,
            reason=normalized_reason,
            source=source,
        )

    def deprecate(
        self,
        asset_id: str,
        *,
        reason: str,
        source: str = "code-library",
    ):
        decision = self.evaluate(
            asset_id,
            reason=reason,
            source=source,
        )

        if not decision.should_deprecate:
            return self.engine.get(asset_id)

        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        asset.metadata = dict(asset.metadata)
        asset.metadata["deprecation"] = {
            "reason": decision.reason,
            "source": decision.source,
        }

        self.engine.store.save(asset)

        return self.engine.deprecate(asset_id)

    def is_deprecated(
        self,
        asset_id: str,
    ) -> bool:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise KeyError(
                f"Code Library asset not found: {asset_id}"
            )

        return (
            asset.lifecycle
            == CodeAssetLifecycle.DEPRECATED.value
        )


deprecation_manager = CodeLibraryDeprecationManager()


__all__ = (
    "CodeAssetDeprecationDecision",
    "CodeLibraryDeprecationManager",
    "deprecation_manager",
)
