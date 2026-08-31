from builder.autonomous_runtime.diagnosis import FailureDiagnosis
from builder.autonomous_runtime.replan import replanner


NAME = "Failure Aware Replanning"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates failure diagnosis is converted into a new planning input."


def run() -> bool:
    try:
        diagnosis = FailureDiagnosis(
            failed=1,
            files=(
                "/tmp/project/app/main.py",
            ),
            issues=(
                {
                    "validator": "python",
                    "severity": "error",
                    "message": "Backend cannot import frontend modules.",
                    "file": "/tmp/project/app/main.py",
                    "line": 12,
                    "column": 4,
                    "code": "",
                    "suggestion": "",
                },
            ),
            validators=("python",),
        )

        result = replanner.replan(
            objective="Fix the application",
            diagnosis=diagnosis,
            attempt=1,
        )

        return (
            result.attempt == 1
            and result.strategy == "correct-python-dependency-boundary"
            and result.files == diagnosis.files
            and result.validators == diagnosis.validators
            and "Fix the application" in result.objective
            and "main.py" in result.objective
            and "Backend cannot import frontend modules." in result.objective
            and "Do not repeat the previous failed approach unchanged." in result.objective
        )

    except Exception:
        return False
