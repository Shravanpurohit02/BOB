from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.retrieval import (
    KnowledgeRetrievalEngine,
)


NAME = "Knowledge Retrieval Integration"
CATEGORY = "Knowledge"
DESCRIPTION = (
    "Validates the explicit retrieval facade while preserving "
    "verified knowledge filtering and deterministic retrieval."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory) / "knowledge"

            learning = KnowledgeLearningEngine(store)

            evidence = KnowledgeEvidence(
                source="v2-t-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Retrieval knowledge validated.",
            )

            reliable = learning.record(
                category="python",
                title="Backend dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                tags=["backend", "dependency", "boundary"],
                language="python",
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                reliable.id,
                evidence=evidence,
            )

            stale = learning.record(
                category="python",
                title="Deprecated dependency boundary",
                content=(
                    "Backend may import frontend modules "
                    "through the deprecated layout."
                ),
                tags=["deprecated", "dependency"],
                language="python",
                confidence=1.0,
                evidence=[evidence],
            )

            retrieval = KnowledgeRetrievalEngine(store)

            all_result = retrieval.search(
                "backend dependency frontend modules",
                limit=10,
                verified_only=False,
            )

            verified_result = retrieval.search(
                "backend dependency frontend modules",
                limit=10,
                verified_only=True,
            )

            reliable_ids = {
                record.id
                for record in verified_result.records
            }

            return (
                reliable.id in reliable_ids
                and verified_result.count >= 1
                and verified_result.query
                == "backend dependency frontend modules"
                and verified_result.verified_only
                and all_result.count >= verified_result.count
                and stale.id in {
                    record.id
                    for record in all_result.records
                }
            )

    except Exception:
        return False
