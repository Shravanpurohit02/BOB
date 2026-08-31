from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetLifecycle
from .supersession import CodeLibrarySupersessionManager


@dataclass(frozen=True)
class CodeAssetVersionPreference:
    """Deterministic preferred-version projection."""

    asset_id: str
    preferred: bool
    version: str
    lifecycle: str
    score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "preferred": self.preferred,
            "version": self.version,
            "lifecycle": self.lifecycle,
            "score": self.score,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class CodeAssetVersionSelection:
    """Selected preferred asset version."""

    asset_id: str
    version: str
    candidates: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "version": self.version,
            "candidates": list(self.candidates),
        }


class CodeLibraryVersionPreference:
    """CL-10.9 deterministic version preference engine.

    Preference is analytical and does not mutate lifecycle state. Promoted,
    non-deprecated assets are preferred over lower lifecycle states, while
    superseded assets are excluded when a valid replacement exists.
    """

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
        supersession: CodeLibrarySupersessionManager | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.supersession = (
            supersession
            or CodeLibrarySupersessionManager(self.engine)
        )

    def rank(
        self,
        candidates: Iterable[CodeAsset],
    ) -> tuple[CodeAssetVersionPreference, ...]:
        items = list(candidates)

        scored: list[CodeAssetVersionPreference] = []

        for asset in items:
            scored.append(
                self._preference(asset)
            )

        return tuple(
            sorted(
                scored,
                key=lambda item: (
                    item.score,
                    self._version_key(item.version),
                    item.asset_id,
                ),
                reverse=True,
            )
        )

    def prefer(
        self,
        candidates: Iterable[CodeAsset],
    ) -> CodeAssetVersionSelection:
        items = list(candidates)

        if not items:
            raise ValueError(
                "At least one version candidate is required"
            )

        ranked = self.rank(items)
        selected = ranked[0]

        return CodeAssetVersionSelection(
            asset_id=selected.asset_id,
            version=selected.version,
            candidates=tuple(
                item.asset_id
                for item in ranked
            ),
        )

    def prefer_by_name(
        self,
        name: str,
    ) -> CodeAssetVersionSelection:
        normalized = str(name).strip().lower()

        if not normalized:
            raise ValueError("Asset name is required")

        candidates = [
            asset
            for asset in self.engine.list_assets()
            if asset.name.strip().lower() == normalized
        ]

        if not candidates:
            raise KeyError(
                f"No Code Library versions found for: {name}"
            )

        return self.prefer(candidates)

    def _preference(
        self,
        asset: CodeAsset,
    ) -> CodeAssetVersionPreference:
        reasons: list[str] = []

        if asset.lifecycle == CodeAssetLifecycle.PROMOTED.value:
            score = 4.0
            reasons.append("promoted")
        elif asset.lifecycle == CodeAssetLifecycle.VALIDATED.value:
            score = 3.0
            reasons.append("validated")
        elif asset.lifecycle == CodeAssetLifecycle.DRAFT.value:
            score = 1.0
            reasons.append("draft")
        else:
            score = 0.0
            reasons.append("deprecated")

        if asset.lifecycle == CodeAssetLifecycle.DEPRECATED.value:
            reasons.append("deprecated")

        if self.supersession.is_superseded(asset.id):
            score -= 3.0
            reasons.append("superseded")
        else:
            reasons.append("current")

        if asset.success_rate > 0:
            score += asset.success_rate
            reasons.append("successful_usage")

        return CodeAssetVersionPreference(
            asset_id=asset.id,
            preferred=score > 0,
            version=asset.version,
            lifecycle=asset.lifecycle,
            score=score,
            reasons=tuple(reasons),
        )

    @staticmethod
    def _version_key(version: str) -> tuple[int, ...]:
        parts: list[int] = []

        for value in str(version).split("."):
            digits = ""

            for char in value:
                if char.isdigit():
                    digits += char
                else:
                    break

            parts.append(
                int(digits or 0)
            )

        while len(parts) < 3:
            parts.append(0)

        return tuple(parts[:3])


version_preference = CodeLibraryVersionPreference()


__all__ = (
    "CodeAssetVersionPreference",
    "CodeAssetVersionSelection",
    "CodeLibraryVersionPreference",
    "version_preference",
)
