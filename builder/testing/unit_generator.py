class UnitTestGenerator:

    def generate(
        self,
        plan,
    ):

        tests = []

        for item in plan:

            if item["type"] != "unit":
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
                    "test_name": f"test_{module}",
                    "body": [
                        "assert True",
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


generator = UnitTestGenerator()
