from __future__ import annotations

from dataclasses import dataclass, field

from builder.engineering.testing.framework import (
    TestReport,
    engineering_test_framework,
)


@dataclass(slots=True)
class RegressionSuite:
    """
    Collection of permanent engineering regression tests.
    """

    name: str

    tests: list[str] = field(default_factory=list)


class RegressionRunner:
    """
    Executes the registered engineering regression suite.
    """

    def __init__(self):
        self.suites: dict[str, RegressionSuite] = {}

    def create_suite(
        self,
        name: str,
    ) -> RegressionSuite:

        suite = RegressionSuite(name=name)

        self.suites[name] = suite

        return suite

    def register(
        self,
        suite: str,
        test_name: str,
        callback,
    ):

        if suite not in self.suites:
            self.create_suite(suite)

        self.suites[suite].tests.append(test_name)

        engineering_test_framework.register(
            test_name,
            callback,
        )

    def run(
        self,
    ) -> TestReport:

        return engineering_test_framework.run()


regression_runner = RegressionRunner()

__all__ = (
    "RegressionRunner",
    "RegressionSuite",
    "regression_runner",
)
