class MultiFilePlanningEngine:

    def plan(
        self,
        repository_graph,
        impact,
        strategy,
    ):

        phases = []

        for module in impact.get(
            "impacted",
            [],
        ):

            node = repository_graph.get(
                module,
                {},
            )

            phases.append(
                {
                    "module": module,
                    "dependencies": len(
                        node.get(
                            "imports",
                            [],
                        )
                    ),
                    "dependents": len(
                        node.get(
                            "imported_by",
                            [],
                        )
                    ),
                    "strategy": strategy[
                        "strategy"
                    ],
                }
            )

        phases.sort(
            key=lambda item: (
                item["dependents"],
                item["dependencies"],
            ),
            reverse=True,
        )

        return phases

    def execution_order(
        self,
        plan,
    ):

        return [
            item["module"]
            for item in plan
        ]


planner = MultiFilePlanningEngine()
