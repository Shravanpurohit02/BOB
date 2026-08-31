from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from .core import KnowledgeRecord, KnowledgeStore


@dataclass(slots=True, frozen=True)
class KnowledgeRetrievalItem:
    record: KnowledgeRecord
    lexical_score: float
    confidence_score: float
    success_score: float
    final_score: float
    matched_tokens: tuple[str, ...]

    def __getitem__(self, key: str) -> Any:
        if key == "id":
            return self.record.id
        if key == "title":
            return self.record.title
        if key == "content":
            return self.record.content
        if key == "category":
            return self.record.category
        if key == "confidence":
            return self.record.confidence
        if key == "success_rate":
            return self.record.success_rate
        if key == "promoted":
            return self.record.promoted
        if key == "lexical_score":
            return self.lexical_score
        if key == "confidence_score":
            return self.confidence_score
        if key == "success_score":
            return self.success_score
        if key == "final_score":
            return self.final_score
        if key == "matched_tokens":
            return self.matched_tokens
        raise KeyError(key)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.record, name)

    def keys(self) -> tuple[str, ...]:
        return (
            "id",
            "title",
            "content",
            "category",
            "confidence",
            "success_rate",
            "promoted",
            "lexical_score",
            "confidence_score",
            "success_score",
            "final_score",
            "matched_tokens",
        )

    def items(self) -> Iterator[tuple[str, Any]]:
        for key in self.keys():
            yield key, self[key]


@dataclass(slots=True, frozen=True)
class KnowledgeRetrievalResult:
    records: tuple[KnowledgeRetrievalItem, ...]
    count: int
    query: str
    verified_only: bool


class KnowledgeRetrievalEngine:
    """
    Explainable deterministic retrieval facade for BOB knowledge.

    Retrieval ranking is based on:
        lexical relevance
        confidence
        historical success rate

    The underlying KnowledgeRecord lifecycle and learning contracts
    remain unchanged.
    """

    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()

    @staticmethod
    def _tokens(query: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    token.strip().lower()
                    for token in query.split()
                    if token.strip()
                }
            )
        )

    @staticmethod
    def _haystack(record: KnowledgeRecord) -> str:
        return " ".join(
            (
                record.title,
                record.content,
                record.category,
                record.language,
                record.framework,
                record.version,
                " ".join(record.tags),
            )
        ).lower()

    def search(
        self,
        query: str,
        *,
        category: str | None = None,
        language: str | None = None,
        limit: int = 10,
        verified_only: bool = False,
    ) -> KnowledgeRetrievalResult:
        tokens = self._tokens(query)
        candidates: list[KnowledgeRetrievalItem] = []

        for record in self.store.all():
            if category and record.category != category:
                continue

            if language and (
                record.language.lower() != language.lower()
            ):
                continue

            if verified_only and not record.verified:
                continue

            haystack = self._haystack(record)

            matched = tuple(
                token
                for token in tokens
                if token in haystack
            )

            if not matched:
                continue

            lexical_score = (
                len(matched) / len(tokens)
                if tokens
                else 0.0
            )

            confidence_score = max(
                0.0,
                min(1.0, float(record.confidence)),
            )

            success_score = max(
                0.0,
                min(1.0, float(record.success_rate)),
            )

            final_score = (
                lexical_score * 0.60
                + confidence_score * 0.20
                + success_score * 0.20
            )

            candidates.append(
                KnowledgeRetrievalItem(
                    record=record,
                    lexical_score=lexical_score,
                    confidence_score=confidence_score,
                    success_score=success_score,
                    final_score=final_score,
                    matched_tokens=matched,
                )
            )

        candidates.sort(
            key=lambda item: (
                item.final_score,
                item.lexical_score,
                item.confidence_score,
                item.success_score,
                item.record.id,
            ),
            reverse=True,
        )

        selected = candidates[
            :max(0, int(limit))
        ]

        return KnowledgeRetrievalResult(
            records=tuple(selected),
            count=len(selected),
            query=query,
            verified_only=verified_only,
        )

    def records(
        self,
        query: str,
        *,
        limit: int = 10,
        verified_only: bool = True,
    ) -> list[KnowledgeRetrievalItem]:
        return list(
            self.search(
                query,
                limit=limit,
                verified_only=verified_only,
            ).records
        )


retrieval = KnowledgeRetrievalEngine()


__all__ = (
    "KnowledgeRetrievalItem",
    "KnowledgeRetrievalResult",
    "KnowledgeRetrievalEngine",
    "retrieval",
)
