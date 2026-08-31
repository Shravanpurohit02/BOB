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


NAME = "Knowledge Retrieval"
CATEGORY = "Knowledge"
DESCRIPTION = (
    "Validates explainable lexical retrieval, confidence and success "
    "ranking, filtering, deterministic ordering and result limits."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            retrieval = KnowledgeRetrievalEngine(store)

            evidence = KnowledgeEvidence(
                source="v2-t-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Retrieval knowledge validated.",
            )

            primary = learning.record(
                category="python",
                title="Backend dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                tags=["python", "architecture"],
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                primary.id,
                evidence=evidence,
            )
            learning.record_success(
                primary.id,
                evidence=evidence,
            )

            secondary = learning.record(
                category="python",
                title="Frontend dependency information",
                content=(
                    "Frontend modules may depend on backend "
                    "services."
                ),
                tags=["frontend"],
                confidence=0.5,
                evidence=[evidence],
            )

            learning.record_success(
                secondary.id,
                evidence=evidence,
            )

            unverified = learning.record(
                category="python",
                title="Unverified dependency pattern",
                content=(
                    "Backend dependencies should be reviewed."
                ),
                confidence=1.0,
            )

            all_results = retrieval.search(
                "backend dependencies frontend modules",
                limit=10,
            )

            verified_results = retrieval.search(
                "backend dependencies frontend modules",
                limit=10,
                verified_only=True,
            )

            limited_results = retrieval.search(
                "backend dependencies frontend modules",
                limit=1,
                verified_only=True,
            )

            primary_match = next(
                (
                    item
                    for item in verified_results.records
                    if item["id"] == primary.id
                ),
                None,
            )

            return (
                all_results.count >= 2
                and verified_results.count == 2
                and limited_results.count == 1
                and primary_match is not None
                and primary_match["final_score"] > 0.0
                and primary_match["lexical_score"] > 0.0
                and primary_match["confidence_score"] == 1.0
                and primary_match["success_score"] == 1.0
                and len(primary_match["matched_tokens"]) >= 1
                and unverified.id not in {
                    item["id"]
                    for item in verified_results.records
                }
                and verified_results.records[0]["final_score"] >=
                verified_results.records[-1]["final_score"]
            )

    except Exception:
        return False
