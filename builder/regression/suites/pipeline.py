from pathlib import Path

from builder.pipeline import engine as pipeline

NAME = "Pipeline"
CATEGORY = "Foundation"
DESCRIPTION = "Validates the engineering pipeline."

EXPECTED_PIPELINE = [
    "changeset",
    "output",
    "semantic",
    "planning",
    "impact",
    "validation",
    "testing",
    "finalization",
]


def run() -> bool:

    try:
        result = pipeline.start(
            "Regression Pipeline Test",
            str(Path.cwd()),
        )

        stages = result.stages

        return stages == EXPECTED_PIPELINE and len(stages) == len(set(stages))

    except Exception:
        return False
