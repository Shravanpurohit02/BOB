from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .autonomous import AutonomousKnowledgeEngine
from .core import KnowledgeEvidence, KnowledgeLearningEngine, KnowledgeStore


@dataclass(slots=True, frozen=True)
class KnowledgeRuntimeContext:
    query: str
    records: tuple[dict[str, Any], ...]
    count: int
    strategy: str
    excluded: int


class KnowledgeRuntimeBridge:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.learning = KnowledgeLearningEngine(self.store)
        self.autonomous = AutonomousKnowledgeEngine(self.store)

    def prepare(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> KnowledgeRuntimeContext:
        result = self.autonomous.search_and_prepare(
            query,
            limit=limit,
            verified_only=True,
        )

        return KnowledgeRuntimeContext(
            query=query,
            records=result.records,
            count=result.count,
            strategy=result.strategy,
            excluded=result.excluded,
        )

    def learn_execution(
        self,
        *,
        category: str,
        title: str,
        content: str,
        source: str,
        validator: str,
        passed: bool,
        workspace: str = "",
        tags: list[str] | None = None,
        language: str = "",
        framework: str = "",
        version: str = "",
    ):
        return self.learning.learn_from_validated_result(
            category=category,
            title=title,
            content=content,
            source=source,
            validator=validator,
            passed=passed,
            workspace=workspace,
            tags=tags,
            language=language,
            framework=framework,
            version=version,
        )

    def learn_success(
        self,
        record_id: str,
        *,
        source: str = "runtime",
        validator: str = "runtime",
        workspace: str = "",
    ):
        evidence = KnowledgeEvidence(
            source=source,
            source_type="runtime_execution",
            reference=workspace,
            validator=validator,
            status="verified",
            message="Runtime execution succeeded.",
        )

        return self.learning.record_success(
            record_id,
            evidence=evidence,
        )

    def learn_failure(
        self,
        record_id: str,
        *,
        source: str = "runtime",
        validator: str = "runtime",
        workspace: str = "",
    ):
        evidence = KnowledgeEvidence(
            source=source,
            source_type="runtime_execution",
            reference=workspace,
            validator=validator,
            status="failed",
            message="Runtime execution failed.",
        )

        return self.learning.record_failure(
            record_id,
            evidence=evidence,
        )


runtime = KnowledgeRuntimeBridge()


__all__ = (
    "KnowledgeRuntimeContext",
    "KnowledgeRuntimeBridge",
    "runtime",
)
