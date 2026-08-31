from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta, timezone

from builder.knowledge.core import (
    KnowledgeEvidence,
    KnowledgeLearningEngine,
    KnowledgeStore,
)
from builder.knowledge.autonomous import (
    AutonomousKnowledgeEngine,
)


NAME = "Knowledge Autonomous Learning"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates that autonomous knowledge selection excludes stale "
    "and conflicting knowledge while retaining reliable knowledge."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            learning = KnowledgeLearningEngine(store)
            autonomous = AutonomousKnowledgeEngine(store)

            evidence = KnowledgeEvidence(
                source="v2-h-regression",
                source_type="regression",
                validator="python",
                status="verified",
                message="Knowledge validated.",
            )

            reliable = learning.record(
                category="python",
                title="Reliable backend boundary",
                content=(
                    "Backend code must not import frontend modules."
                ),
                confidence=1.0,
                evidence=[evidence],
            )

            learning.record_success(
                reliable.id,
                evidence=evidence,
            )

            # A knowledge pattern becomes reliable only after the
            # existing quality contract observes at least two
            # successful uses.
            learning.record_success(
                reliable.id,
            )

            reliable = store.get(reliable.id)

            if reliable is None:
                return False

            stale = learning.record(
                category="python",
                title="Old backend boundary",
                content=(
                    "Use the deprecated frontend import boundary."
                ),
                confidence=1.0,
                evidence=[evidence],
            )

            stale = store.get(stale.id)

            if stale is None:
                return False

            stale.updated_at = (
                datetime.now(timezone.utc)
                - timedelta(days=365)
            ).isoformat()

            import json
            from dataclasses import asdict

            store._file(stale.id).write_text(
                json.dumps(
                    asdict(stale),
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            stale = store.get(stale.id)

            if stale is None:
                return False

            result = autonomous.search_and_prepare(
                "backend boundary frontend modules",
                limit=10,
                verified_only=True,
            )

            selected_ids = {
                item["id"]
                for item in result.records
            }

            return (
                result.count == 1
                and result.strategy == "knowledge_guided_repair"
                and reliable.id in selected_ids
                and stale.id not in selected_ids
                and result.excluded >= 1
            )

    except Exception:
        return False
