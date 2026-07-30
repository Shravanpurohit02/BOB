class RegressionTestGenerator:

    def generate(
        self,
        changed_files,
    ):

        tests = []

        for path in changed_files:

            module = (
                path
                .split("/")[-1]
                .replace(".py", "")
            )

            tests.append(
                {
                    "module": module,
                    "file": path,
                    "test_name": f"test_regression_{module}",
                    "scope": "regression",
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


generator = RegressionTestGenerator()
