from typing import ClassVar

from builder.regression.models import RegressionResult


class RegressionEngine:
    EXPECTED_PIPELINE: ClassVar[tuple[str, ...]] = (
        "changeset",
        "output",
        "semantic",
        "planning",
        "impact",
        "validation",
        "testing",
        "finalization",
    )

    def run(self):

        from builder.regression.suites import SUITES

        result = RegressionResult()

        for name, suite in SUITES.items():
            try:
                passed = bool(suite())

            except Exception:
                passed = False

            self._record(
                result,
                name,
                passed,
            )

        return result

    def _record(self, result, name, passed):
        result.total += 1
        if passed:
            result.passed += 1
            result.tests.append(f"{name}: PASS")
        else:
            result.failed += 1
            result.tests.append(f"{name}: FAIL")


engine = RegressionEngine()
