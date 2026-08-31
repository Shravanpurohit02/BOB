from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ResourceIndexEntry:
    asset_id: str
    terms: tuple[str, ...]
    metadata: dict

    def __post_init__(self) -> None:
        if not self.asset_id.strip():
            raise ValueError("asset_id must not be empty")

        normalized = tuple(
            sorted(
                dict.fromkeys(
                    term.strip().lower()
                    for term in self.terms
                    if term and term.strip()
                )
            )
        )

        object.__setattr__(
            self,
            "terms",
            normalized,
        )

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "terms": list(self.terms),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ResourceIndexResult:
    term: str
    asset_ids: tuple[str, ...]
    total_matches: int

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "asset_ids": list(self.asset_ids),
            "total_matches": self.total_matches,
        }


class CodeLibraryResourceIndex:
    """
    Compact in-memory inverted index for local/offline Code Library
    retrieval.

    The index stores normalized term -> asset-id mappings and a compact
    reverse mapping for incremental updates/removal.
    """

    def __init__(self) -> None:
        self._forward: dict[str, tuple[str, ...]] = {}
        self._reverse: dict[str, tuple[str, ...]] = {}
        self._metadata: dict[str, dict] = {}

    @staticmethod
    def _normalize_term(term: str) -> str:
        if not isinstance(term, str):
            raise TypeError("term must be a string")

        return term.strip().lower()

    @classmethod
    def _normalize_terms(
        cls,
        terms: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = []

        for term in terms:
            value = cls._normalize_term(term)

            if value:
                normalized.append(value)

        return tuple(
            sorted(
                dict.fromkeys(normalized)
            )
        )

    @staticmethod
    def _merge_sorted(
        values: Iterable[str],
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                dict.fromkeys(
                    value
                    for value in values
                    if value
                )
            )
        )

    def add(
        self,
        asset_id: str,
        terms: Iterable[str],
        *,
        metadata: dict | None = None,
    ) -> ResourceIndexEntry:
        if not isinstance(asset_id, str):
            raise TypeError(
                "asset_id must be a string"
            )

        asset_id = asset_id.strip()

        if not asset_id:
            raise ValueError(
                "asset_id must not be empty"
            )

        normalized = self._normalize_terms(terms)

        self.remove(asset_id)

        for term in normalized:
            self._forward[term] = self._merge_sorted(
                (
                    *self._forward.get(term, ()),
                    asset_id,
                )
            )

        self._reverse[asset_id] = normalized
        self._metadata[asset_id] = dict(
            metadata or {}
        )

        return ResourceIndexEntry(
            asset_id=asset_id,
            terms=normalized,
            metadata=dict(
                metadata or {}
            ),
        )

    def add_many(
        self,
        entries: Iterable[ResourceIndexEntry],
    ) -> tuple[ResourceIndexEntry, ...]:
        normalized = tuple(entries)

        for entry in normalized:
            if not isinstance(
                entry,
                ResourceIndexEntry,
            ):
                raise TypeError(
                    "entries must contain ResourceIndexEntry"
                )

        for entry in normalized:
            self.add(
                entry.asset_id,
                entry.terms,
                metadata=entry.metadata,
            )

        return normalized

    def get(
        self,
        asset_id: str,
    ) -> ResourceIndexEntry | None:
        if not isinstance(asset_id, str):
            raise TypeError(
                "asset_id must be a string"
            )

        asset_id = asset_id.strip()

        if asset_id not in self._reverse:
            return None

        return ResourceIndexEntry(
            asset_id=asset_id,
            terms=self._reverse[asset_id],
            metadata=self._metadata.get(
                asset_id,
                {},
            ),
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    def lookup(
        self,
        term: str,
    ) -> ResourceIndexResult:
        normalized = self._normalize_term(term)

        if not normalized:
            raise ValueError(
                "term must not be empty"
            )

        asset_ids = self._forward.get(
            normalized,
            (),
        )

        return ResourceIndexResult(
            term=normalized,
            asset_ids=asset_ids,
            total_matches=len(asset_ids),
        )

    def lookup_many(
        self,
        terms: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = self._normalize_terms(
            terms
        )

        matched = set()

        for term in normalized:
            matched.update(
                self._forward.get(
                    term,
                    (),
                )
            )

        return tuple(sorted(matched))

    def intersection(
        self,
        terms: Iterable[str],
    ) -> tuple[str, ...]:
        normalized = self._normalize_terms(
            terms
        )

        if not normalized:
            return ()

        sets = [
            set(
                self._forward.get(
                    term,
                    (),
                )
            )
            for term in normalized
        ]

        if not sets:
            return ()

        return tuple(
            sorted(
                set.intersection(*sets)
            )
        )

    def union(
        self,
        terms: Iterable[str],
    ) -> tuple[str, ...]:
        return self.lookup_many(terms)

    def remove(
        self,
        asset_id: str,
    ) -> ResourceIndexEntry | None:
        if not isinstance(asset_id, str):
            raise TypeError(
                "asset_id must be a string"
            )

        asset_id = asset_id.strip()

        terms = self._reverse.pop(
            asset_id,
            None,
        )

        if terms is None:
            return None

        metadata = self._metadata.pop(
            asset_id,
            {},
        )

        for term in terms:
            current = self._forward.get(
                term,
                (),
            )

            remaining = tuple(
                value
                for value in current
                if value != asset_id
            )

            if remaining:
                self._forward[term] = remaining
            else:
                self._forward.pop(
                    term,
                    None,
                )

        return ResourceIndexEntry(
            asset_id=asset_id,
            terms=terms,
            metadata=metadata,
        )

    def update(
        self,
        asset_id: str,
        terms: Iterable[str],
        *,
        metadata: dict | None = None,
    ) -> ResourceIndexEntry:
        return self.add(
            asset_id,
            terms,
            metadata=metadata,
        )

    def clear(self) -> None:
        self._forward.clear()
        self._reverse.clear()
        self._metadata.clear()

    def count(self) -> int:
        return len(self._reverse)

    def term_count(self) -> int:
        return len(self._forward)

    def asset_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(self._reverse)
        )

    def terms(self) -> tuple[str, ...]:
        return tuple(
            sorted(self._forward)
        )

    def export_payload(self) -> dict:
        return {
            "assets": {
                asset_id: {
                    "terms": list(
                        self._reverse[asset_id]
                    ),
                    "metadata": dict(
                        self._metadata.get(
                            asset_id,
                            {},
                        )
                    ),
                }
                for asset_id in sorted(
                    self._reverse
                )
            }
        }

    def import_payload(
        self,
        payload: dict,
        *,
        replace: bool = False,
    ) -> None:
        if not isinstance(payload, dict):
            raise TypeError(
                "payload must be a dictionary"
            )

        assets = payload.get(
            "assets",
            {},
        )

        if not isinstance(assets, dict):
            raise ValueError(
                "payload assets must be a dictionary"
            )

        if replace:
            self.clear()

        for asset_id, data in assets.items():
            if not isinstance(data, dict):
                raise ValueError(
                    "asset index data must be a dictionary"
                )

            self.add(
                asset_id,
                data.get("terms", ()),
                metadata=data.get(
                    "metadata",
                    {},
                ),
            )

    def to_dict(self) -> dict:
        return {
            "asset_count": self.count(),
            "term_count": self.term_count(),
            "assets": {
                asset_id: self.get(
                    asset_id
                ).to_dict()
                for asset_id in self.asset_ids()
            },
            "terms": {
                term: list(
                    self._forward[term]
                )
                for term in self.terms()
            },
        }


__all__ = [
    "ResourceIndexEntry",
    "ResourceIndexResult",
    "CodeLibraryResourceIndex",
]
