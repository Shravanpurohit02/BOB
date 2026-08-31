from pathlib import Path
from tempfile import TemporaryDirectory

from builder.autonomous_runtime.diagnosis import FailureDiagnosis
from builder.autonomous_runtime.replan import ReplanEngine
from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.decision import KnowledgeAwareDecisionEngine


NAME = "Knowledge Runtime Context"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates end-to-end propagation of validated knowledge through "
    "retrieval, decision, replanning and repair context."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            workspace = Path(directory)

            store = KnowledgeStore()
            store.root = workspace / "knowledge"

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
                source="v2-u-runtime-context-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Validated engineering pattern.",
            )

            learning.record_success(
                record.id,
                evidence=evidence,
            )

            learning.record_success(
                record.id,
            )

            record = store.get(record.id)

            if record is None:
                return False

            diagnosis = FailureDiagnosis(
                failed=1,
                files=("backend/main.py",),
                issues=(
                    {
                        "validator": "python",
                        "severity": "error",
                        "message": (
                            "Backend cannot import "
                            "frontend modules."
                        ),
                        "file": "backend/main.py",
                        "line": 12,
                        "column": 4,
                        "code": "PY001",
                        "suggestion": "",
                    },
                ),
                validators=("python",),
            )

            learned = learning.search(
                "Backend cannot import frontend modules",
                limit=5,
                verified_only=True,
            )

            selected = KnowledgeAwareDecisionEngine(
                store
            ).select(learned)

            learned_context = [
                {
                    "id": item["id"],
                    "title": item["title"],
                    "content": item["content"],
                    "confidence": item["confidence"],
                    "success_rate": item["success_rate"],
                    "category": item["category"],
                    "promoted": item["promoted"],
                }
                for item in selected.records
            ]

            replanned = ReplanEngine().replan(
                objective="Fix the application",
                diagnosis=diagnosis,
                attempt=1,
                learned_context=learned_context,
            )

            repair_context = diagnosis.as_context(
                objective=replanned.objective,
                workspace=str(workspace),
            )

            repair_context["learned_context"] = (
                list(learned_context)
            )

            repair_context["knowledge_count"] = (
                len(learned_context)
            )

            repair_context["knowledge_strategy"] = (
                selected.strategy
            )

            return (
                len(learned) == 1
                and selected.count == 1
                and selected.reliable is True
                and selected.strategy
                == "knowledge_guided_repair"
                and bool(learned_context)
                and learned_context[0]["id"] == record.id
                and learned_context[0]["title"]
                == "Python dependency boundary"
                and learned_context[0]["confidence"] == 1.0
                and learned_context[0]["success_rate"] == 1.0
                and learned_context[0]["promoted"] is True
                and bool(replanned.learned_context)
                and replanned.learned_context[0]["id"]
                == record.id
                and replanned.learned_context[0]["title"]
                == "Python dependency boundary"
                and "LEARNED KNOWLEDGE"
                in replanned.objective
                and "Python dependency boundary"
                in replanned.objective
                and "Backend dependencies must not import frontend modules."
                in replanned.objective
                and repair_context["knowledge_count"] == 1
                and repair_context["knowledge_strategy"]
                == "knowledge_guided_repair"
                and bool(
                    repair_context["learned_context"]
                )
                and repair_context["learned_context"][0]["id"]
                == record.id
            )

    except Exception:
        return False
