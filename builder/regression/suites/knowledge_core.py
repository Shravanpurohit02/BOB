from tempfile import TemporaryDirectory
from pathlib import Path

from builder.knowledge.core import (
    KnowledgeStore,
    KnowledgeLearningEngine,
)

NAME = "Knowledge Core"
CATEGORY = "Knowledge"
DESCRIPTION = "Validates persistent knowledge storage, search, and learning feedback."


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            engine = KnowledgeLearningEngine(store)

            record = engine.record(
                category="code",
                title="Python dependency boundary",
                content="Backend dependencies must not import frontend modules.",
                tags=["python", "architecture"],
                language="python",
                confidence=0.5,
            )

            loaded = store.get(record.id)

            results = engine.search(
                "python dependency boundary"
            )

            engine.record_success(record.id)

            learned = store.get(record.id)

            return (
                loaded is not None
                and len(results) == 1
                and learned is not None
                and learned.successes == 1
                and learned.uses == 1
                and learned.confidence == 1.0
            )

    except Exception:
        return False
