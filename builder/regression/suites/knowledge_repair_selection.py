from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.repair import (
    KnowledgeRepairSelector,
)


NAME = "Knowledge Repair Selection"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates that reliable learned knowledge changes the "
    "autonomous repair strategy."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            selector = KnowledgeRepairSelector(store)

            standard = selector.select(
                "Fix an unrelated database problem",
            )

            evidence = KnowledgeEvidence(
                source="v2-n-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Repair pattern validated.",
            )

            record = learning.record(
                category="python",
                title="Dependency boundary repair",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                tags=["python", "dependency", "repair"],
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                record.id,
                evidence=evidence,
            )

            learning.record_success(record.id)

            guided = selector.select(
                "Fix the Python dependency boundary",
                query="python dependency boundary repair",
            )

            return (
                standard.strategy == "standard_repair"
                and standard.knowledge_count == 0
                and guided.strategy
                == "knowledge_guided_repair"
                and guided.knowledge_count == 1
                and guided.knowledge[0]["id"]
                == record.id
                and guided.knowledge[0]["promoted"]
            )

    except Exception:
        return False
