class IntelligentTestPlanner:

    TEST_TYPES = {
        "planner": "unit",
        "executor": "integration",
        "validator": "unit",
        "runtime": "integration",
        "provider": "integration",
        "regression": "regression",
    }

    def plan(
        self,
        impacted_files,
    ):

        plan = []

        for order, path in enumerate(
            impacted_files,
            start=1,
        ):

            plan.append(
                {
                    "order": order,
                    "file": path,
                    "type": self._type(path),
                    "priority": self._priority(path),
                }
            )

        return plan

    def _type(
        self,
        path,
    ):

        name = path.lower()

        for key, value in self.TEST_TYPES.items():

            if key in name:
                return value

        return "unit"

    def _priority(
        self,
        path,
    ):

        name = path.lower()

        if (
            "provider" in name
            or "runtime" in name
        ):
            return "critical"

        if (
            "executor" in name
            or "planner" in name
        ):
            return "high"

        return "normal"

    def summary(
        self,
        plan,
    ):

        return {
            "tests": len(plan),
            "critical": sum(
                item["priority"] == "critical"
                for item in plan
            ),
            "integration": sum(
                item["type"] == "integration"
                for item in plan
            ),
        }


planner = IntelligentTestPlanner()
