class IntegrationTestGenerator:

    def generate(
        self,
        plan,
    ):

        tests = []

        for item in plan:

            if item["type"] != "integration":
                continue

            module = (
                item["file"]
                .split("/")[-1]
                .replace(".py", "")
            )

            tests.append(
                {
                    "module": module,
                    "file": item["file"],
                    "test_name": f"test_integration_{module}",
                    "steps": [
                        "initialize",
                        "execute",
                        "validate",
                    ],
                }
            )

        return tests

    def summary(
        self,
        tests,
    ):

        return {
            "generated": len(tests),
            "modules": [
                test["module"]
                for test in tests
            ],
        }


generator = IntegrationTestGenerator()
