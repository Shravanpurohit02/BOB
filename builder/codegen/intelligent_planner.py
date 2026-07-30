class IntelligentCodePlanner:

    def plan(
        self,
        objective,
        strategy,
        impacted_files,
    ):

        phases = []

        for order, path in enumerate(
            impacted_files,
            start=1,
        ):

            phases.append(
                {
                    "order": order,
                    "file": path,
                    "objective": objective,
                    "strategy": strategy,
                    "action": self._action(path),
                }
            )

        return phases

    def _action(
        self,
        path,
    ):

        name = path.lower()

        if "test" in name:
            return "update-tests"

        if "validator" in name:
            return "extend-validation"

        if "planner" in name:
            return "extend-planning"

        if "executor" in name:
            return "extend-execution"

        return "modify"

    def summary(
        self,
        plan,
    ):

        return {
            "files": len(plan),
            "actions": sorted(
                {
                    item["action"]
                    for item in plan
                }
            ),
        }


planner = IntelligentCodePlanner()
