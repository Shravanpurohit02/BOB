from __future__ import annotations

from dataclasses import dataclass

from .local_retrieval import (
    CodeLibraryLocalRetrievalEngine,
    LocalRetrievalQuery,
)
from .requirement_understanding import (
    ConstructionRequirement,
    RequirementUnderstandingResult,
)


@dataclass(frozen=True)
class RequirementRetrievalResult:
    requirement_name: str
    query: LocalRetrievalQuery
    candidates: tuple
    best_candidate: object | None
    score: float
    compatible: bool
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "requirement_name": self.requirement_name,
            "query": self.query.to_dict(),
            "candidates": [
                candidate.to_dict()
                if hasattr(candidate, "to_dict")
                else candidate
                for candidate in self.candidates
            ],
            "best_candidate": (
                self.best_candidate.to_dict()
                if hasattr(
                    self.best_candidate,
                    "to_dict",
                )
                else self.best_candidate
            ),
            "score": self.score,
            "compatible": self.compatible,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryRequirementRetrieval:
    """
    Integrates CL-15.1 requirement understanding with the
    CL-14.4 local Code Library retrieval engine.
    """

    def __init__(
        self,
        retrieval_engine: CodeLibraryLocalRetrievalEngine,
    ) -> None:
        if not isinstance(
            retrieval_engine,
            CodeLibraryLocalRetrievalEngine,
        ):
            raise TypeError(
                "retrieval_engine must be "
                "CodeLibraryLocalRetrievalEngine"
            )

        self.retrieval_engine = retrieval_engine

    @staticmethod
    def build_query(
        requirement: ConstructionRequirement,
    ) -> LocalRetrievalQuery:
        if not isinstance(
            requirement,
            ConstructionRequirement,
        ):
            raise TypeError(
                "requirement must be "
                "ConstructionRequirement"
            )

        return LocalRetrievalQuery(
            asset_type="component",
            language=requirement.language,
            framework=requirement.framework,
            runtime=requirement.runtime,
            platform=requirement.platform,
            tags=(
                requirement.tags
                + requirement.capabilities
            ),
            dependencies=requirement.dependencies,
        )

    def retrieve(
        self,
        requirement: ConstructionRequirement,
        *,
        limit: int | None = None,
    ) -> RequirementRetrievalResult:
        if not isinstance(
            requirement,
            ConstructionRequirement,
        ):
            raise TypeError(
                "requirement must be "
                "ConstructionRequirement"
            )

        query = self.build_query(
            requirement
        )

        result = self.retrieval_engine.retrieve(
            query,
        )

        all_candidates = tuple(
            result.candidates
        )

        if limit is not None:
            if not isinstance(limit, int):
                raise TypeError(
                    "limit must be an integer or None"
                )

            if limit < 0:
                raise ValueError(
                    "limit must be >= 0"
                )

            candidates = all_candidates[:limit]
        else:
            candidates = all_candidates

        best_candidate = (
            candidates[0]
            if candidates
            else None
        )

        compatible = bool(
            candidates
        )

        reasons: list[str] = [
            "requirement_query_built",
        ]

        if candidates:
            reasons.append(
                "library_candidates_retrieved"
            )
            reasons.append(
                "best_candidate_selected"
            )
        else:
            reasons.append(
                "no_library_candidates_found"
            )

        score = (
            float(
                getattr(
                    best_candidate,
                    "score",
                    0.0,
                )
            )
            if best_candidate is not None
            else 0.0
        )

        return RequirementRetrievalResult(
            requirement_name=requirement.name,
            query=query,
            candidates=candidates,
            best_candidate=best_candidate,
            score=score,
            compatible=compatible,
            reasons=tuple(reasons),
            metadata={
                "candidate_count": len(
                    candidates
                ),
                "requested_limit": limit,
                "capability_count": len(
                    requirement.capabilities
                ),
                "dependency_count": len(
                    requirement.dependencies
                ),
            },
        )

    def retrieve_understood(
        self,
        result: RequirementUnderstandingResult,
        *,
        limit: int | None = None,
    ) -> RequirementRetrievalResult:
        if not isinstance(
            result,
            RequirementUnderstandingResult,
        ):
            raise TypeError(
                "result must be "
                "RequirementUnderstandingResult"
            )

        if not result.complete:
            raise ValueError(
                "requirement understanding must be complete"
            )

        return self.retrieve(
            result.requirement,
            limit=limit,
        )


__all__ = [
    "RequirementRetrievalResult",
    "CodeLibraryRequirementRetrieval",
]
