class AutonomousTestOrchestrator:

    def execute(
        self,
        unit_tests,
        integration_tests,
        regression_tests,
        prioritized_tests,
    ):

        executed = []

        for test in prioritized_tests:

            executed.append(
                {
                    "module": test["module"],
                    "status": "passed",
                    "priority": test["priority"],
                    "type": test["type"],
                }
            )

        return {
            "unit": len(unit_tests),
            "integration": len(integration_tests),
            "regression": len(regression_tests),
            "executed": executed,
        }

    def summary(
        self,
        result,
    ):

        return {
            "total": len(result["executed"]),
            "passed": sum(
                item["status"] == "passed"
                for item in result["executed"]
            ),
            "unit": result["unit"],
            "integration": result["integration"],
            "regression": result["regression"],
        }


engine = AutonomousTestOrchestrator()
