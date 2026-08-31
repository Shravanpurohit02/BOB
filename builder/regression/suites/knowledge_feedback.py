from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.feedback import (
    AutonomousKnowledgeFeedbackEngine,
)


NAME = "Knowledge Feedback"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates that autonomous execution outcomes feed back into "
    "persistent knowledge quality and usage statistics."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            feedback = AutonomousKnowledgeFeedbackEngine(store)

            evidence = KnowledgeEvidence(
                source="v2-i-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Initial validation succeeded.",
            )

            record = learning.record(
                category="python",
                title="Autonomous import boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                confidence=1.0,
                evidence=[evidence],
            )

            first = feedback.record_success(
                record.id,
                validator="python",
                workspace="regression-success",
            )

            second = feedback.record_success(
                record.id,
                validator="python",
                workspace="regression-success",
            )

            failed = feedback.record_failure(
                record.id,
                validator="python",
                workspace="regression-failure",
            )

            stored = store.get(record.id)

            if (
                first is None
                or second is None
                or failed is None
                or stored is None
            ):
                return False

            return (
                first.successes == 1
                and second.successes == 2
                and second.promoted
                and failed.successes == 2
                and failed.failures == 1
                and failed.promoted
                and stored.uses == 3
                and stored.successes == 2
                and stored.failures == 1
                and stored.success_rate > 0.0
                and len(stored.evidence) >= 4
            )

    except Exception:
        return False
