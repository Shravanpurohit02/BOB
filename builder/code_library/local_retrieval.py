from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .offline_catalog import (
    CodeLibraryOfflineCatalog,
    OfflineCatalogContext,
    OfflineCatalogEntry,
    OfflineCatalogResult,
)


@dataclass(frozen=True)
class LocalRetrievalQuery:
    query: str = ""
    asset_type: str = ""
    language: str = ""
    framework: str = ""
    runtime: str = ""
    platform: str = ""
    tags: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    offline_only: bool = True
    limit: int = 10
    context: OfflineCatalogContext | None = None

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise ValueError("limit must be positive")

    def normalized_tags(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                dict.fromkeys(
                    value.strip().lower()
                    for value in self.tags
                    if value and value.strip()
                )
            )
        )

    def normalized_dependencies(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                dict.fromkeys(
                    value.strip()
                    for value in self.dependencies
                    if value and value.strip()
                )
            )
        )

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "asset_type": self.asset_type,
            "language": self.language,
            "framework": self.framework,
            "runtime": self.runtime,
            "platform": self.platform,
            "tags": list(self.normalized_tags()),
            "dependencies": list(
                self.normalized_dependencies()
            ),
            "offline_only": self.offline_only,
            "limit": self.limit,
            "context": (
                None
                if self.context is None
                else self.context.to_dict()
            ),
        }


@dataclass(frozen=True)
class LocalRetrievalCandidate:
    asset_id: str
    score: float
    matched_fields: tuple[str, ...]
    rank: int
    entry: OfflineCatalogEntry

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "score": self.score,
            "matched_fields": list(self.matched_fields),
            "rank": self.rank,
            "entry": self.entry.to_dict(),
        }


@dataclass(frozen=True)
class LocalRetrievalResult:
    candidates: tuple[LocalRetrievalCandidate, ...]
    query: LocalRetrievalQuery
    total_matches: int
    returned_count: int
    compatible: bool
    offline: bool
    reasons: tuple[str, ...]
    metadata: dict

    @property
    def asset_ids(self) -> tuple[str, ...]:
        return tuple(
            candidate.asset_id
            for candidate in self.candidates
        )

    @property
    def best(self) -> LocalRetrievalCandidate | None:
        return (
            self.candidates[0]
            if self.candidates
            else None
        )

    def to_dict(self) -> dict:
        return {
            "candidates": [
                candidate.to_dict()
                for candidate in self.candidates
            ],
            "query": self.query.to_dict(),
            "total_matches": self.total_matches,
            "returned_count": self.returned_count,
            "compatible": self.compatible,
            "offline": self.offline,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryLocalRetrievalEngine:
    """
    Deterministic local retrieval engine over the offline catalog.

    Retrieval is entirely local and performs no network access.
    Candidate scores are based on exact matches across the requested
    query dimensions. Ties are resolved by asset_id.
    """

    def __init__(
        self,
        catalog: CodeLibraryOfflineCatalog,
    ) -> None:
        if not isinstance(
            catalog,
            CodeLibraryOfflineCatalog,
        ):
            raise TypeError(
                "catalog must be CodeLibraryOfflineCatalog"
            )

        self.catalog = catalog

    @staticmethod
    def _score_candidate(
        entry: OfflineCatalogEntry,
        query: LocalRetrievalQuery,
    ) -> tuple[float, tuple[str, ...]]:
        score = 0.0
        matched: list[str] = []

        needle = query.query.strip().lower()

        if needle:
            if needle == entry.asset_id.lower():
                score += 10.0
                matched.append("asset_id")
            elif needle == entry.name.lower():
                score += 9.0
                matched.append("name")
            else:
                searchable = (
                    f"{entry.asset_id} "
                    f"{entry.name} "
                    f"{entry.description} "
                    f"{entry.language} "
                    f"{entry.framework} "
                    f"{entry.runtime} "
                    f"{' '.join(entry.tags)}"
                ).lower()

                if needle in searchable:
                    score += 4.0
                    matched.append("query")

        if query.asset_type:
            if (
                entry.asset_type.strip().lower()
                == query.asset_type.strip().lower()
            ):
                score += 2.0
                matched.append("asset_type")

        if query.language:
            if (
                entry.language.strip().lower()
                == query.language.strip().lower()
            ):
                score += 2.0
                matched.append("language")

        if query.framework:
            if (
                entry.framework.strip().lower()
                == query.framework.strip().lower()
            ):
                score += 2.0
                matched.append("framework")

        if query.runtime:
            if (
                entry.runtime.strip().lower()
                == query.runtime.strip().lower()
            ):
                score += 2.0
                matched.append("runtime")

        if query.platform:
            if (
                query.platform.strip().lower()
                in entry.platforms
            ):
                score += 2.0
                matched.append("platform")

        requested_tags = set(
            query.normalized_tags()
        )

        if requested_tags:
            matched_tags = requested_tags.intersection(
                set(entry.tags)
            )

            if matched_tags:
                score += 2.0 * (
                    len(matched_tags)
                    / len(requested_tags)
                )
                matched.append("tags")

        requested_dependencies = set(
            query.normalized_dependencies()
        )

        if requested_dependencies:
            matched_dependencies = (
                requested_dependencies.intersection(
                    set(entry.dependencies)
                )
            )

            if matched_dependencies:
                score += 1.0 * (
                    len(matched_dependencies)
                    / len(requested_dependencies)
                )
                matched.append("dependencies")

        return (
            round(score, 6),
            tuple(matched),
        )

    def retrieve(
        self,
        query: LocalRetrievalQuery,
    ) -> LocalRetrievalResult:
        if not isinstance(
            query,
            LocalRetrievalQuery,
        ):
            raise TypeError(
                "query must be LocalRetrievalQuery"
            )

        candidates: list[
            LocalRetrievalCandidate
        ] = []

        for entry in self.catalog.list_entries():
            if not entry.matches(
                query=query.query,
                asset_type=query.asset_type,
                language=query.language,
                framework=query.framework,
                runtime=query.runtime,
                platform=query.platform,
                tags=query.normalized_tags(),
                offline_only=query.offline_only,
            ):
                continue

            score, matched_fields = (
                self._score_candidate(
                    entry,
                    query,
                )
            )

            candidates.append(
                LocalRetrievalCandidate(
                    asset_id=entry.asset_id,
                    score=score,
                    matched_fields=matched_fields,
                    rank=0,
                    entry=entry,
                )
            )

        candidates.sort(
            key=lambda candidate: (
                -candidate.score,
                candidate.asset_id,
            )
        )

        ranked = tuple(
            LocalRetrievalCandidate(
                asset_id=candidate.asset_id,
                score=candidate.score,
                matched_fields=candidate.matched_fields,
                rank=index,
                entry=candidate.entry,
            )
            for index, candidate in enumerate(
                candidates[: query.limit],
                start=1,
            )
        )

        reasons: list[str] = [
            "local_catalog_retrieval",
        ]

        if query.offline_only:
            reasons.append(
                "offline_only_retrieval"
            )

        if query.query:
            reasons.append("query_match")

        if query.context is not None:
            reasons.append(
                "retrieval_context_present"
            )

        if ranked:
            reasons.append(
                "retrieval_candidates_found"
            )
        else:
            reasons.append(
                "retrieval_candidates_not_found"
            )

        return LocalRetrievalResult(
            candidates=ranked,
            query=query,
            total_matches=len(candidates),
            returned_count=len(ranked),
            compatible=bool(ranked),
            offline=True,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "catalog_count": self.catalog.count(),
                "matched_count": len(candidates),
                "returned_count": len(ranked),
                "limit": query.limit,
            },
        )

    def retrieve_best(
        self,
        query: LocalRetrievalQuery,
    ) -> LocalRetrievalCandidate | None:
        return self.retrieve(query).best

    def retrieve_asset(
        self,
        asset_id: str,
    ) -> LocalRetrievalCandidate | None:
        if not asset_id.strip():
            raise ValueError(
                "asset_id must not be empty"
            )

        entry = self.catalog.get(asset_id)

        if entry is None:
            return None

        return LocalRetrievalCandidate(
            asset_id=entry.asset_id,
            score=10.0,
            matched_fields=("asset_id",),
            rank=1,
            entry=entry,
        )

    def retrieve_many(
        self,
        asset_ids: Iterable[str],
    ) -> tuple[
        LocalRetrievalCandidate,
        ...,
    ]:
        normalized = tuple(
            dict.fromkeys(
                asset_id.strip()
                for asset_id in asset_ids
                if asset_id and asset_id.strip()
            )
        )

        candidates = []

        for asset_id in normalized:
            candidate = self.retrieve_asset(
                asset_id
            )

            if candidate is not None:
                candidates.append(candidate)

        return tuple(candidates)


__all__ = [
    "LocalRetrievalQuery",
    "LocalRetrievalCandidate",
    "LocalRetrievalResult",
    "CodeLibraryLocalRetrievalEngine",
]
