class AutonomousCodeValidator:

    REQUIRED_KEYS = (
        "file",
        "mode",
        "generated",
        "patch",
    )

    def validate(
        self,
        outputs,
    ):

        results = []

        for output in outputs:

            passed = all(
                key in output
                for key in self.REQUIRED_KEYS
            )

            results.append(
                {
                    "file": output.get(
                        "file",
                        "",
                    ),
                    "passed": passed,
                }
            )

        return results

    def summary(
        self,
        results,
    ):

        total = len(results)

        passed = sum(
            item["passed"]
            for item in results
        )

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success": passed == total,
        }


validator = AutonomousCodeValidator()
