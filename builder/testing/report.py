class TestReport:

    def create(self, results):

        return {
            "tests": len(results),
            "passed": sum(r.success for r in results),
            "failed": sum(not r.success for r in results),
            "duration": round(
                sum(r.duration for r in results),
                6,
            ),
        }

report = TestReport()
