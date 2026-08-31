from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.replanning import (
    KnowledgeReplanningEngine,
)


NAME = "Knowledge Replanning"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates that reliable learned knowledge can be converted "
    "into autonomous replanning context."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            replanning = KnowledgeReplanningEngine(store)

            evidence = KnowledgeEvidence(
                source="v2-m-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Repair pattern validated.",
            )

            record = learning.record(
                category="python",
                title="Python dependency boundary repair",
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

            prepared = replanning.prepare(
                "python dependency boundary repair",
                limit=5,
            )

            enriched = replanning.enrich(
                "Fix the application",
                query="python dependency boundary repair",
            )

            ids = {
                item["id"]
                for item in prepared.records
            }

            return (
                prepared.count == 1
                and prepared.strategy == "knowledge_guided_repair"
                and record.id in ids
                and enriched["knowledge_count"] == 1
                and enriched["knowledge_strategy"]
                == "knowledge_guided_repair"
                and enriched["knowledge"][0]["id"]
                == record.id
            )

    except Exception:
        return False
