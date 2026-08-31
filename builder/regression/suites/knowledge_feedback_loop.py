from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.feedback import (
    AutonomousKnowledgeFeedback,
)


NAME = "Knowledge Feedback Loop"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates that autonomous execution feedback updates "
    "knowledge and influences the next repair attempt."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            feedback = AutonomousKnowledgeFeedback(store)

            evidence = KnowledgeEvidence(
                source="v2-p-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Knowledge pattern validated.",
            )

            record = learning.record(
                category="python",
                title="Dependency boundary repair",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                tags=["python", "repair"],
                confidence=0.5,
                evidence=[evidence],
            )

            first = feedback.record_outcome(
                record.id,
                passed=True,
                source="v2-p-first-attempt",
                validator="python",
            )

            if first is None:
                return False

            after_first = store.get(record.id)

            if after_first is None:
                return False

            second = feedback.record_outcome(
                record.id,
                passed=True,
                source="v2-p-second-attempt",
                validator="python",
            )

            if second is None:
                return False

            after_second = store.get(record.id)

            if after_second is None:
                return False

            next_attempt = feedback.apply_to_next_attempt(
                "Fix Python dependency boundary",
                query="python dependency boundary repair",
            )

            failed = feedback.record_outcome(
                record.id,
                passed=False,
                source="v2-p-failure-attempt",
                validator="python",
            )

            if failed is None:
                return False

            after_failure = store.get(record.id)

            if after_failure is None:
                return False

            return (
                first.outcome == "success"
                and first.successes >= 1
                and second.outcome == "success"
                and after_second.successes >= 2
                and after_second.promoted
                and next_attempt["strategy"]
                == "knowledge_guided_repair"
                and next_attempt["knowledge_count"] >= 1
                and record.id in {
                    item["id"]
                    for item in next_attempt["knowledge"]
                }
                and failed.outcome == "failure"
                and after_failure.failures == 1
                and after_failure.uses >= 3
            )

    except Exception:
        return False
