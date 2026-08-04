from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


@dataclass(slots=True)
class TestCase:
    name: str
    callback: callable


@dataclass(slots=True)
class TestResult:
    name: str
    success: bool
    duration: float
    message: str = ""


@dataclass(slots=True)
class TestReport:
    total: int = 0
    passed: int = 0
    failed: int = 0
    results: list[TestResult] = field(default_factory=list)


class EngineeringTestFramework:
    def __init__(self):
        self._tests: list[TestCase] = []

    def register(
        self,
        name: str,
        callback,
    ):
        self._tests.append(
            TestCase(
                name=name,
                callback=callback,
            )
        )

    def run(self) -> TestReport:

        report = TestReport()

        for test in self._tests:

            start = perf_counter()

            try:
                test.callback()

                success = True
                message = ""

            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as exc:  # noqa: BLE001
                success = False
                message = str(exc)

            duration = perf_counter() - start

            report.results.append(
                TestResult(
                    name=test.name,
                    success=success,
                    duration=duration,
                    message=message,
                )
            )

        report.total = len(report.results)
        report.passed = sum(r.success for r in report.results)
        report.failed = report.total - report.passed

        return report


engineering_test_framework = EngineeringTestFramework()

__all__ = (
    "EngineeringTestFramework",
    "TestCase",
    "TestReport",
    "TestResult",
    "engineering_test_framework",
)
