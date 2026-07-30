import time

from builder.testing.result import TestResult

class TestRunner:

    def run(self, tests):

        results = []

        for test in tests:

            start = time.perf_counter()

            try:
                test.callback()

                results.append(
                    TestResult(
                        name=test.name,
                        success=True,
                        duration=round(
                            time.perf_counter()-start,
                            6,
                        ),
                    )
                )

            except Exception as exc:

                results.append(
                    TestResult(
                        name=test.name,
                        success=False,
                        duration=round(
                            time.perf_counter()-start,
                            6,
                        ),
                        message=str(exc),
                    )
                )

        return results

runner = TestRunner()
