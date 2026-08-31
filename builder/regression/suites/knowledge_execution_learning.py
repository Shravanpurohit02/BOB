from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)


NAME = "Knowledge Execution Learning"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates automatic learning from successful and failed "
    "validated execution outcomes."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)

            success = learning.learn_from_validated_result(
                category="autonomous-execution",
                title="Autonomous execution success",
                content=(
                    "Autonomous execution completed with "
                    "validation success."
                ),
                source="autonomous_runtime",
                validator="python",
                passed=True,
                workspace="/tmp/project",
                tags=[
                    "autonomous",
                    "execution",
                    "validation",
                ],
            )

            failure = learning.learn_from_validated_result(
                category="autonomous-execution",
                title="Autonomous execution failure",
                content=(
                    "Autonomous execution produced a "
                    "validation failure."
                ),
                source="autonomous_runtime",
                validator="python",
                passed=False,
                workspace="/tmp/project",
                tags=[
                    "autonomous",
                    "execution",
                    "validation",
                ],
            )

            loaded_success = store.get(success.id)
            loaded_failure = store.get(failure.id)

            verified = any(
                item.status == "verified"
                for item in success.evidence
            )

            failed = any(
                item.status == "failed"
                for item in failure.evidence
            )

            return (
                loaded_success is not None
                and loaded_failure is not None
                and loaded_success.successes == 1
                and loaded_success.uses == 1
                and loaded_success.confidence == 1.0
                and loaded_failure.failures == 1
                and loaded_failure.uses == 1
                and verified
                and failed
            )

    except Exception:
        return False
