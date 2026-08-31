from pathlib import Path
from tempfile import TemporaryDirectory

from builder.knowledge.acquisition import (
    AutonomousKnowledgeAcquisition,
)
from builder.knowledge.core import KnowledgeStore


NAME = "Knowledge Acquisition"
CATEGORY = "Autonomous"
DESCRIPTION = (
    "Validates autonomous acquisition of knowledge from "
    "validated execution results."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = KnowledgeStore()
            store.root = Path(directory)

            acquisition = AutonomousKnowledgeAcquisition(store)

            rejected = acquisition.acquire(
                category="python",
                title="Rejected execution pattern",
                content="This execution failed validation.",
                source="v2-l-regression",
                validator="python",
                passed=False,
            )

            if rejected.acquired:
                return False

            accepted = acquisition.acquire(
                category="python",
                title="Validated dependency boundary",
                content=(
                    "Backend dependencies must not import "
                    "frontend modules."
                ),
                source="v2-l-regression",
                validator="python",
                passed=True,
                tags=["python", "architecture"],
            )

            if not accepted.acquired:
                return False

            if not accepted.record_id:
                return False

            stored = store.get(accepted.record_id)

            if stored is None:
                return False

            validation = acquisition.acquire_from_validation(
                category="python",
                title="Validated runtime boundary",
                content=(
                    "Runtime validation confirms the "
                    "dependency boundary."
                ),
                validation={
                    "failed": 0,
                    "passed": True,
                },
                source="v2-l-validation",
                validator="python",
            )

            failed_validation = acquisition.acquire_from_validation(
                category="python",
                title="Failed runtime boundary",
                content="Validation failed.",
                validation={
                    "failed": 1,
                    "passed": False,
                },
                source="v2-l-validation",
                validator="python",
            )

            return (
                accepted.acquired
                and stored.successes >= 1
                and stored.verified
                and validation.acquired
                and not failed_validation.acquired
                and len(store.all()) == 2
            )

    except Exception:
        return False
