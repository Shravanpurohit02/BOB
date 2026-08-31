from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import KnowledgeEvidence, KnowledgeLearningEngine, KnowledgeStore
from .repair import KnowledgeRepairSelector


@dataclass(slots=True, frozen=True)
class KnowledgeFeedbackResult:
    record_id: str
    outcome: str
    confidence: float
    successes: int
    failures: int
    promoted: bool
    strategy: str
    knowledge_count: int


class AutonomousKnowledgeFeedback:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
    ):
        self.store = store or KnowledgeStore()
        self.learning = KnowledgeLearningEngine(self.store)
        self.selector = KnowledgeRepairSelector(self.store)

    def record_outcome(
        self,
        record_id: str,
        *,
        passed: bool,
        source: str = "autonomous-runtime",
        validator: str = "runtime",
        workspace: str = "",
    ) -> KnowledgeFeedbackResult | None:
        evidence = KnowledgeEvidence(
            source=source,
            source_type="autonomous_feedback",
            reference=workspace,
            validator=validator,
            status="verified" if passed else "failed",
            message=(
                "Autonomous execution succeeded."
                if passed
                else "Autonomous execution failed."
            ),
        )

        if passed:
            record = self.learning.record_success(
                record_id,
                evidence=evidence,
            )
        else:
            record = self.learning.record_failure(
                record_id,
                evidence=evidence,
            )

        if record is None:
            return None

        return self._result(
            record,
            passed=passed,
        )

    def record_success(
        self,
        record_id: str,
        *,
        source: str = "autonomous-runtime",
        validator: str = "runtime",
        workspace: str = "",
    ) -> KnowledgeFeedbackResult | None:
        return self.record_outcome(
            record_id,
            passed=True,
            source=source,
            validator=validator,
            workspace=workspace,
        )

    def record_failure(
        self,
        record_id: str,
        *,
        source: str = "autonomous-runtime",
        validator: str = "runtime",
        workspace: str = "",
    ) -> KnowledgeFeedbackResult | None:
        return self.record_outcome(
            record_id,
            passed=False,
            source=source,
            validator=validator,
            workspace=workspace,
        )

    def _result(
        self,
        record,
        *,
        passed: bool,
    ) -> KnowledgeFeedbackResult:
        decision = self.selector.select(
            record.title + " " + record.content,
        )

        return KnowledgeFeedbackResult(
            record_id=record.id,
            outcome="success" if passed else "failure",
            confidence=record.confidence,
            successes=record.successes,
            failures=record.failures,
            promoted=record.promoted,
            strategy=decision.strategy,
            knowledge_count=decision.knowledge_count,
        )

    def apply_to_next_attempt(
        self,
        objective: str,
        *,
        query: str | None = None,
        limit: int = 5,
    ) -> dict[str, Any]:
        decision = self.selector.select(
            objective,
            query=query,
            limit=limit,
        )

        return {
            "objective": objective,
            "strategy": decision.strategy,
            "knowledge_count": decision.knowledge_count,
            "knowledge": list(decision.knowledge),
            "reason": decision.reason,
        }


AutonomousKnowledgeFeedbackEngine = AutonomousKnowledgeFeedback

feedback = AutonomousKnowledgeFeedback()


__all__ = (
    "KnowledgeFeedbackResult",
    "AutonomousKnowledgeFeedback",
    "AutonomousKnowledgeFeedbackEngine",
    "feedback",
)
