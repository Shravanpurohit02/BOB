class CodeGenerationStrategyEngine:

    def strategy(
        self,
        objective,
        repository_strategy,
        plan,
    ):

        actions = []

        for item in plan:

            actions.append(
                {
                    "file": item["file"],
                    "action": item["action"],
                    "mode": self._mode(
                        item["action"],
                    ),
                }
            )

        return {
            "objective": objective,
            "strategy": repository_strategy,
            "files": len(plan),
            "actions": actions,
        }

    def _mode(
        self,
        action,
    ):

        mapping = {
            "modify":"patch",
            "extend-planning":"extend",
            "extend-execution":"extend",
            "extend-validation":"extend",
            "update-tests":"test",
        }

        return mapping.get(
            action,
            "patch",
        )


engine = CodeGenerationStrategyEngine()
