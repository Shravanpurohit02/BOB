from __future__ import annotations

from dataclasses import dataclass
import re

from .models import CodeAsset, CodeAssetLifecycle
from .provenance import CodeLibraryProvenance
from .store import CodeLibraryStore


@dataclass(slots=True, frozen=True)
class CodeLibraryRetrievalItem:
    asset: CodeAsset
    lexical_score: float
    metadata_score: float
    quality_score: float
    final_score: float
    matched_tokens: tuple[str, ...]
    reasons: tuple[str, ...]

    def __getitem__(self, key: str):
        if key == "asset":
            return self.asset
        if key == "id":
            return self.asset.id
        if key == "name":
            return self.asset.name
        if key == "asset_type":
            return self.asset.asset_type
        if key == "language":
            return self.asset.language
        if key == "framework":
            return self.asset.framework
        if key == "runtime":
            return self.asset.runtime
        if key == "lifecycle":
            return self.asset.lifecycle
        if key == "lexical_score":
            return self.lexical_score
        if key == "metadata_score":
            return self.metadata_score
        if key == "quality_score":
            return self.quality_score
        if key == "final_score":
            return self.final_score
        if key == "matched_tokens":
            return self.matched_tokens
        if key == "reasons":
            return self.reasons
        raise KeyError(key)

    def __getattr__(self, name: str):
        return getattr(self.asset, name)


@dataclass(slots=True, frozen=True)
class CodeLibraryRetrievalResult:
    records: tuple[CodeLibraryRetrievalItem, ...]
    count: int
    query: str
    limit: int
    include_draft: bool
    include_deprecated: bool


class CodeLibraryRetrievalEngine:
    """
    Deterministic, explainable retrieval facade for BOB Code Library assets.

    CL-4 retrieves canonical CodeAsset records without creating a second
    source of truth. Catalog and store contracts remain authoritative.

    Ranking dimensions:
        lexical relevance: 60%
        metadata relevance: 20%
        asset quality: 20%

    By default only validated/promoted assets with valid provenance are
    eligible. Draft assets require explicit include_draft=True and
    deprecated assets require explicit include_deprecated=True.
    """

    LEXICAL_WEIGHT = 0.60
    METADATA_WEIGHT = 0.20
    QUALITY_WEIGHT = 0.20

    _TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")

    def __init__(self, store: CodeLibraryStore | None = None) -> None:
        self.store = store or CodeLibraryStore()

    @classmethod
    def _tokens(cls, text: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    token.lower()
                    for token in cls._TOKEN_PATTERN.findall(str(text or ""))
                    if token.strip()
                }
            )
        )

    @classmethod
    def _haystack(cls, asset: CodeAsset) -> str:
        values = [
            asset.id,
            asset.name,
            asset.description,
            asset.asset_type,
            asset.language,
            asset.framework,
            asset.runtime,
            asset.version,
            asset.parent_id,
            *asset.tags,
            *asset.capabilities,
            *asset.dependencies,
            *asset.entrypoints,
        ]

        for item in asset.files:
            values.extend((item.path, item.language))

        return " ".join(str(value) for value in values).lower()

    @staticmethod
    def _metadata_score(
        asset: CodeAsset,
        tokens: tuple[str, ...],
    ) -> tuple[float, tuple[str, ...]]:
        if not tokens:
            return 0.0, ()

        fields = {
            "name": asset.name,
            "capability": " ".join(asset.capabilities),
            "tag": " ".join(asset.tags),
            "framework": asset.framework,
            "language": asset.language,
            "runtime": asset.runtime,
            "type": asset.asset_type,
            "dependency": " ".join(asset.dependencies),
        }

        matched: set[str] = set()
        reasons: list[str] = []

        for label, value in fields.items():
            haystack = str(value).lower()
            for token in tokens:
                if token in haystack:
                    matched.add(token)
                    reasons.append(label)

        score = min(
            1.0,
            len(matched) / len(tokens),
        )

        return score, tuple(sorted(set(reasons)))

    @staticmethod
    def _quality_score(asset: CodeAsset) -> float:
        success = max(
            0.0,
            min(1.0, float(asset.success_rate)),
        )

        lifecycle_bonus = {
            CodeAssetLifecycle.DRAFT.value: 0.0,
            CodeAssetLifecycle.VALIDATED.value: 0.5,
            CodeAssetLifecycle.PROMOTED.value: 1.0,
            CodeAssetLifecycle.DEPRECATED.value: 0.0,
        }.get(asset.lifecycle, 0.0)

        provenance_valid, _ = CodeLibraryProvenance.validate_asset(asset)
        provenance_score = 1.0 if provenance_valid else 0.0

        return (
            success * 0.50
            + lifecycle_bonus * 0.30
            + provenance_score * 0.20
        )

    @staticmethod
    def _eligible(
        asset: CodeAsset,
        *,
        include_draft: bool,
        include_deprecated: bool,
    ) -> bool:
        if asset.lifecycle == CodeAssetLifecycle.DEPRECATED.value:
            return include_deprecated

        if asset.lifecycle == CodeAssetLifecycle.DRAFT.value:
            return include_draft

        return asset.lifecycle in {
            CodeAssetLifecycle.VALIDATED.value,
            CodeAssetLifecycle.PROMOTED.value,
        }

    def search(
        self,
        query: str,
        *,
        asset_type: str | None = None,
        language: str | None = None,
        framework: str | None = None,
        runtime: str | None = None,
        lifecycle: str | None = None,
        tag: str | None = None,
        capability: str | None = None,
        dependency: str | None = None,
        parent_id: str | None = None,
        limit: int = 10,
        include_draft: bool = False,
        include_deprecated: bool = False,
    ) -> CodeLibraryRetrievalResult:
        tokens = self._tokens(query)
        candidates: list[CodeLibraryRetrievalItem] = []

        filters = {
            "asset_type": str(asset_type or "").strip().lower(),
            "language": str(language or "").strip().lower(),
            "framework": str(framework or "").strip().lower(),
            "runtime": str(runtime or "").strip().lower(),
            "lifecycle": str(lifecycle or "").strip().lower(),
            "tag": str(tag or "").strip().lower(),
            "capability": str(capability or "").strip().lower(),
            "dependency": str(dependency or "").strip().lower(),
            "parent_id": str(parent_id or "").strip(),
        }

        for asset in self.store.all():
            if not self._eligible(
                asset,
                include_draft=include_draft,
                include_deprecated=include_deprecated,
            ):
                continue

            if filters["asset_type"] and asset.asset_type.lower() != filters["asset_type"]:
                continue
            if filters["language"] and asset.language.lower() != filters["language"]:
                continue
            if filters["framework"] and asset.framework.lower() != filters["framework"]:
                continue
            if filters["runtime"] and asset.runtime.lower() != filters["runtime"]:
                continue
            if filters["lifecycle"] and asset.lifecycle.lower() != filters["lifecycle"]:
                continue
            if filters["parent_id"] and asset.parent_id != filters["parent_id"]:
                continue
            if filters["tag"] and filters["tag"] not in {str(x).lower() for x in asset.tags}:
                continue
            if filters["capability"] and filters["capability"] not in {
                str(x).lower() for x in asset.capabilities
            }:
                continue
            if filters["dependency"] and filters["dependency"] not in {
                str(x).lower() for x in asset.dependencies
            }:
                continue

            haystack = self._haystack(asset)

            if tokens:
                matched = tuple(
                    token for token in tokens if token in haystack
                )
                if not matched:
                    continue

                lexical_score = len(matched) / len(tokens)
            else:
                matched = ()
                lexical_score = 0.0

            metadata_score, metadata_reasons = self._metadata_score(
                asset,
                tokens,
            )
            quality_score = self._quality_score(asset)

            final_score = (
                lexical_score * self.LEXICAL_WEIGHT
                + metadata_score * self.METADATA_WEIGHT
                + quality_score * self.QUALITY_WEIGHT
            )

            reasons = list(metadata_reasons)

            if asset.lifecycle == CodeAssetLifecycle.PROMOTED.value:
                reasons.append("promoted")

            if asset.success_rate > 0:
                reasons.append("successful_usage")

            provenance_valid, _ = CodeLibraryProvenance.validate_asset(asset)
            if provenance_valid:
                reasons.append("valid_provenance")

            candidates.append(
                CodeLibraryRetrievalItem(
                    asset=asset,
                    lexical_score=lexical_score,
                    metadata_score=metadata_score,
                    quality_score=quality_score,
                    final_score=final_score,
                    matched_tokens=matched,
                    reasons=tuple(sorted(set(reasons))),
                )
            )

        candidates.sort(
            key=lambda item: (
                item.final_score,
                item.lexical_score,
                item.metadata_score,
                item.quality_score,
                item.asset.success_rate,
                item.asset.id,
            ),
            reverse=True,
        )

        selected = candidates[:max(0, int(limit))]

        return CodeLibraryRetrievalResult(
            records=tuple(selected),
            count=len(selected),
            query=query,
            limit=max(0, int(limit)),
            include_draft=include_draft,
            include_deprecated=include_deprecated,
        )

    def retrieve(
        self,
        query: str,
        *,
        limit: int = 10,
        **filters,
    ) -> list[CodeLibraryRetrievalItem]:
        return list(
            self.search(
                query,
                limit=limit,
                **filters,
            ).records
        )


retrieval = CodeLibraryRetrievalEngine()


__all__ = (
    "CodeLibraryRetrievalEngine",
    "CodeLibraryRetrievalItem",
    "CodeLibraryRetrievalResult",
    "retrieval",
)
