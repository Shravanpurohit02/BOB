from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.decision import (
    KnowledgeAwareDecisionEngine,
)


NAME = "Knowledge Aware Decision"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates that autonomous decisions preferentially use "
    "reliable and promotable knowledge."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            decision = KnowledgeAwareDecisionEngine(store)

            evidence = KnowledgeEvidence(
                source="knowledge-aware-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Pattern validated.",
            )

            reliable = learning.record(
                category="python",
                title="Reliable import boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                reliable.id,
                evidence=evidence,
            )
            learning.record_success(reliable.id)

            reliable = store.get(reliable.id)

            if reliable is None:
                return False

            weak = learning.record(
                category="python",
                title="Unverified pattern",
                content="This pattern has not been validated.",
                confidence=0.2,
            )

            selected = decision.select(
                [reliable, weak]
            )

            return (
                selected.count == 1
                and selected.reliable
                and selected.strategy == "knowledge_guided_repair"
                and selected.records[0]["id"] == reliable.id
                and selected.records[0]["promoted"]
                and weak.id not in {
                    item["id"]
                    for item in selected.records
                }
            )

    except Exception:
        return False
