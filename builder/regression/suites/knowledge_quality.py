from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.quality import KnowledgeQualityEngine


NAME = "Knowledge Quality"
CATEGORY = "Knowledge"
DESCRIPTION = (
    "Validates evidence-aware quality evaluation, promotion, "
    "demotion and reliability decisions."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            quality = KnowledgeQualityEngine(store)

            weak = learning.record(
                category="python",
                title="Weak pattern",
                content="Unverified engineering assumption.",
                confidence=0.2,
            )

            weak_quality = quality.evaluate(weak)

            evidence = KnowledgeEvidence(
                source="knowledge-quality-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Pattern independently validated.",
            )

            strong = learning.record(
                category="python",
                title="Reliable dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                strong.id,
                evidence=evidence,
            )

            learning.record_success(
                strong.id,
            )

            promoted = quality.promote(strong.id)
            strong_quality = quality.evaluate_id(strong.id)

            if promoted is None or strong_quality is None:
                return False

            reliable = quality.reliable(promoted)

            quality.demote(strong.id)

            demoted = store.get(strong.id)

            return (
                not weak_quality.eligible_for_promotion
                and not weak_quality.eligible_for_retrieval
                and strong_quality.verified
                and strong_quality.successes == 2
                and strong_quality.failures == 0
                and strong_quality.success_rate == 1.0
                and strong_quality.eligible_for_promotion
                and promoted.promoted
                and reliable
                and demoted is not None
                and not demoted.promoted
            )

    except Exception:
        return False
