from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.consolidation import (
    KnowledgeConsolidationEngine,
)
from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)


NAME = "Knowledge Consolidation"
CATEGORY = "Knowledge"
DESCRIPTION = (
    "Validates duplicate knowledge detection, consolidation, "
    "evidence preservation and execution-stat aggregation."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            consolidation = KnowledgeConsolidationEngine(store)

            evidence = KnowledgeEvidence(
                source="consolidation-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Pattern validated.",
            )

            first = learning.record(
                category="python",
                title="Backend import boundary",
                content=(
                    "Backend modules must not import "
                    "frontend modules."
                ),
                tags=["python", "imports"],
                confidence=0.8,
                evidence=[evidence],
                provenance="execution-a",
            )

            second = learning.record(
                category="python",
                title="Python backend dependency boundary",
                content=(
                    "Python backend code must not import "
                    "frontend modules."
                ),
                tags=["architecture", "imports"],
                confidence=1.0,
                evidence=[evidence],
                provenance="execution-b",
            )

            learning.record_success(
                first.id,
                evidence=evidence,
            )

            learning.record_success(
                second.id,
                evidence=evidence,
            )

            primary_before = max(
                [first, second],
                key=lambda item: item.confidence,
            )

            result = consolidation.consolidate(
                primary_before,
                threshold=0.50,
            )

            primary = store.get(
                result.primary_id
            )

            remaining = store.all()

            return (
                result.changed
                and len(result.merged_ids) == 1
                and primary is not None
                and primary.uses == 2
                and primary.successes == 2
                and primary.confidence == 1.0
                and len(primary.evidence) >= 2
                and len(remaining) == 1
            )

    except Exception:
        return False
