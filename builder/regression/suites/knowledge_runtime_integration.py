from tempfile import TemporaryDirectory
from pathlib import Path

from builder.autonomous_runtime.diagnosis import FailureDiagnosis
from builder.autonomous_runtime.replan import replanner
from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)


NAME = "Knowledge Runtime Integration"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates learned knowledge retrieval and failure-aware replanning."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)

            record = learning.record(
                category="python",
                title="Python dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                tags=["python", "architecture", "imports"],
                language="python",
                confidence=1.0,
            )

            evidence = KnowledgeEvidence(
                source="knowledge-runtime-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Validated engineering pattern.",
            )

            learning.record_success(
                record.id,
                evidence=evidence,
            )

            diagnosis = FailureDiagnosis(
                failed=1,
                files=(
                    "/tmp/project/backend/main.py",
                ),
                issues=(
                    {
                        "validator": "python",
                        "severity": "error",
                        "message": (
                            "Backend cannot import "
                            "frontend modules."
                        ),
                        "file": (
                            "/tmp/project/backend/main.py"
                        ),
                        "line": 12,
                        "column": 4,
                    },
                ),
                validators=("python",),
            )

            learned = learning.search(
                "Backend cannot import frontend modules",
                verified_only=True,
                limit=5,
            )

            result = replanner.replan(
                objective="Fix the application",
                diagnosis=diagnosis,
                attempt=1,
                learned_context=[
                    {
                        "title": item.title,
                        "content": item.content,
                        "confidence": item.confidence,
                        "success_rate": item.success_rate,
                        "category": item.category,
                    }
                    for item in learned
                ],
            )

            return (
                len(learned) == 1
                and "LEARNED KNOWLEDGE" in result.objective
                and "Python dependency boundary"
                in result.objective
                and result.learned_context
            )

    except Exception:
        return False
