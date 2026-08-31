from builder.testing import engine as testing

NAME = "Autonomous Testing"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates autonomous testing pipeline."


def run() -> bool:

    try:
        result = testing.execute(
            ".",
        )

        if result is None:
            return False

        if hasattr(result, "passed") and hasattr(result, "failed"):
            return result.failed == 0

        if hasattr(result, "success"):
            return bool(result.success)

        if isinstance(result, dict):
            if "failed" in result:
                return result["failed"] == 0
            return bool(result.get("success", False))

        return True

    except Exception:
        return False
