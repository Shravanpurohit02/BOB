from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import KnowledgeEvidence, KnowledgeLearningEngine, KnowledgeStore
from .repair import KnowledgeRepairSelector


@dataclass(slots=True, frozen=True)
class KnowledgeAwareRepairResult:
    strategy: str
    knowledge_count: int
    selected_knowledge: tuple[dict[str, Any], ...]
    learned: bool
    record_id: str | None
    reason: str


class KnowledgeAwareAutonomousRepair:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.learning = KnowledgeLearningEngine(self.store)
        self.selector = KnowledgeRepairSelector(self.store)

    def plan(
        self,
        objective: str,
        *,
        query: str | None = None,
        limit: int = 5,
    ) -> KnowledgeAwareRepairResult:
        decision = self.selector.select(
            objective,
            query=query,
            limit=limit,
        )

        return KnowledgeAwareRepairResult(
            strategy=decision.strategy,
            knowledge_count=decision.knowledge_count,
            selected_knowledge=decision.knowledge,
            learned=False,
            record_id=None,
            reason=decision.reason,
        )

    def learn_and_plan(
        self,
        *,
        objective: str,
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
        query: str | None = None,
        limit: int = 5,
    ) -> KnowledgeAwareRepairResult:
        if not passed:
            return self.plan(
                objective,
                query=query,
                limit=limit,
            )

        evidence = KnowledgeEvidence(
            source=source,
            source_type="autonomous_repair",
            reference=workspace,
            validator=validator,
            status="verified",
            message="Repair execution validated.",
        )

        record = self.learning.record(
            category=category,
            title=title,
            content=content,
            tags=tags,
            language=language,
            framework=framework,
            version=version,
            provenance=source,
            evidence=[evidence],
            confidence=1.0,
        )

        self.learning.record_success(
            record.id,
            evidence=evidence,
        )

        self.learning.record_success(
            record.id,
        )

        decision = self.selector.select(
            objective,
            query=query,
            limit=limit,
        )

        return KnowledgeAwareRepairResult(
            strategy=decision.strategy,
            knowledge_count=decision.knowledge_count,
            selected_knowledge=decision.knowledge,
            learned=True,
            record_id=record.id,
            reason=(
                "Validated repair knowledge learned and "
                "made available to the next repair decision."
            ),
        )


e2e = KnowledgeAwareAutonomousRepair()


__all__ = (
    "KnowledgeAwareRepairResult",
    "KnowledgeAwareAutonomousRepair",
    "e2e",
)
