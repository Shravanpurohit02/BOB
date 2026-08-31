from builder.autonomous_runtime.diagnosis import FailureDiagnosis
from builder.autonomous_runtime.replan import ReplanEngine


NAME = "Knowledge-Aware Replanning"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates learned knowledge propagation into failure-aware replanning."


def run() -> bool:
    try:
        diagnosis = FailureDiagnosis(
            failed=1,
            files=("backend/main.py",),
            issues=(
                {
                    "validator": "python",
                    "severity": "error",
                    "message": "Backend cannot import frontend modules.",
                    "file": "backend/main.py",
                    "line": 12,
                    "column": 4,
                    "code": "PY001",
                    "suggestion": "",
                },
            ),
            validators=("python",),
        )

        learned = [
            {
                "id": "knowledge-1",
                "title": "Python dependency boundary",
                "content": "Backend dependencies must not import frontend modules.",
                "confidence": 1.0,
                "success_rate": 1.0,
            },
        ]

        result = ReplanEngine().replan(
            objective="Fix the application",
            diagnosis=diagnosis,
            attempt=1,
            learned_context=learned,
        )

        metadata = result.as_metadata()

        return (
            result.strategy == "correct-python-dependency-boundary"
            and result.learned_context == tuple(learned)
            and metadata["learned_context"] == learned
            and "LEARNED KNOWLEDGE" in result.objective
            and "Python dependency boundary" in result.objective
            and "Backend dependencies must not import frontend modules." in result.objective
            and "confidence=1.0" in result.objective
            and "success_rate=1.0" in result.objective
        )

    except Exception:
        return False
