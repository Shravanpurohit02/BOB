class TestPrioritizationEngine:

    PRIORITY = {
        "critical": 300,
        "high": 200,
        "normal": 100,
        "low": 50,
    }

    TYPE_BONUS = {
        "regression": 30,
        "integration": 20,
        "unit": 10,
    }

    def prioritize(
        self,
        tests,
    ):

        ranked = []

        for test in tests:

            score = (
                self.PRIORITY.get(
                    test.get(
                        "priority",
                        "normal",
                    ),
                    100,
                )
                +
                self.TYPE_BONUS.get(
                    test.get(
                        "type",
                        "unit",
                    ),
                    0,
                )
            )

            item = dict(test)
            item["score"] = score

            ranked.append(item)

        ranked.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return ranked

    def summary(
        self,
        ranked,
    ):

        return {
            "tests": len(ranked),
            "highest": (
                ranked[0]["score"]
                if ranked
                else 0
            ),
            "first": (
                ranked[0]["module"]
                if ranked
                else None
            ),
        }


engine = TestPrioritizationEngine()
