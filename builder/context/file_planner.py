class IntelligentFilePlanner:

    def plan(
        self,
        impact,
        architecture,
        repository_graph,
    ):

        plan = []

        hubs = set(
            architecture.get(
                "hub_modules",
                [],
            )
        )

        for module in impact.get(
            "impacted",
            [],
        ):

            node = repository_graph.get(
                module,
                {},
            )

            priority = 100

            if module in impact.get(
                "changed",
                [],
            ):
                priority += 100

            priority += len(
                node.get(
                    "imported_by",
                    [],
                )
            ) * 10

            if module in hubs:
                priority += 50

            plan.append(
                {
                    "path": module,
                    "priority": priority,
                    "imports": len(
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
                }
            )

        plan.sort(
            key=lambda item: item["priority"],
            reverse=True,
        )

        return plan


planner = IntelligentFilePlanner()
