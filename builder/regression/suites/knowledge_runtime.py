from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.runtime import KnowledgeRuntimeBridge


NAME = "Knowledge Runtime"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates runtime knowledge preparation and execution feedback."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = __import__(
                "builder.knowledge.core",
                fromlist=["KnowledgeStore"],
            ).KnowledgeStore()

            store.root = Path(directory)

            runtime = KnowledgeRuntimeBridge(store)

            record = runtime.learn_execution(
                category="python",
                title="Runtime dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                source="v2-k-regression",
                validator="python",
                passed=True,
                tags=["python", "architecture"],
            )

            loaded = store.get(record.id)

            if loaded is None:
                return False

            runtime.learn_success(
                record.id,
                source="v2-k-runtime",
                validator="python",
            )

            context = runtime.prepare(
                "backend dependency frontend modules",
                limit=10,
            )

            selected = {
                item["id"]
                for item in context.records
            }

            learned = store.get(record.id)

            return (
                learned is not None
                and learned.successes >= 2
                and learned.uses >= 2
                and record.id in selected
                and context.count == 1
                and context.strategy == "knowledge_guided_repair"
                and context.excluded == 0
            )

    except Exception:
        return False
