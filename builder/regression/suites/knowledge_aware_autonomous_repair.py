from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.core import KnowledgeStore
from builder.knowledge.e2e import (
    KnowledgeAwareAutonomousRepair,
)


NAME = "Knowledge-Aware Autonomous Repair"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates the complete knowledge-aware repair loop from "
    "validated execution through learning and repair selection."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            repair = KnowledgeAwareAutonomousRepair(store)

            initial = repair.plan(
                "Fix Python dependency boundary",
                query="python dependency boundary repair",
            )

            learned = repair.learn_and_plan(
                objective="Fix Python dependency boundary",
                category="python",
                title="Dependency boundary repair",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                source="v2-o-regression",
                validator="python",
                passed=True,
                tags=[
                    "python",
                    "dependency",
                    "repair",
                ],
                query="python dependency boundary repair",
            )

            stored = (
                store.get(learned.record_id)
                if learned.record_id
                else None
            )

            final = repair.plan(
                "Fix Python dependency boundary",
                query="python dependency boundary repair",
            )

            selected_ids = {
                item["id"]
                for item in final.selected_knowledge
            }

            return (
                initial.strategy == "standard_repair"
                and initial.knowledge_count == 0
                and learned.learned
                and learned.record_id is not None
                and stored is not None
                and stored.successes >= 2
                and stored.uses >= 2
                and stored.verified
                and learned.strategy
                == "knowledge_guided_repair"
                and final.strategy
                == "knowledge_guided_repair"
                and final.knowledge_count == 1
                and learned.record_id in selected_ids
            )

    except Exception:
        return False
