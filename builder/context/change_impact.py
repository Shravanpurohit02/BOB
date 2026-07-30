class ChangeImpactAnalyzer:

    def analyze(
        self,
        repository_graph,
        changed_modules,
    ):

        impacted = set()
        queue = list(changed_modules)

        while queue:

            module = queue.pop(0)

            if module in impacted:
                continue

            impacted.add(module)

            node = repository_graph.get(
                module,
                {},
            )

            queue.extend(
                node.get(
                    "imported_by",
                    [],
                )
            )

        direct = set(changed_modules)

        indirect = impacted - direct

        return {
            "changed": sorted(direct),
            "impacted": sorted(impacted),
            "indirect": sorted(indirect),
            "count": len(impacted),
        }


engine = ChangeImpactAnalyzer()
