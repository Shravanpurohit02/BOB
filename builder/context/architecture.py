class ArchitectureAnalyzer:

    def analyze(
        self,
        repository_graph,
    ):

        report = {
            "leaf_modules": [],
            "hub_modules": [],
            "isolated_modules": [],
            "statistics": {},
        }

        total_edges = 0

        for module, node in repository_graph.items():

            imports = len(
                node.get(
                    "imports",
                    [],
                )
            )

            imported_by = len(
                node.get(
                    "imported_by",
                    [],
                )
            )

            degree = imports + imported_by

            total_edges += degree

            if degree == 0:
                report["isolated_modules"].append(
                    module
                )

            elif imports == 0:
                report["leaf_modules"].append(
                    module
                )

            if imported_by >= 2:
                report["hub_modules"].append(
                    module
                )

        report["statistics"] = {
            "modules": len(repository_graph),
            "edges": total_edges,
            "leaf_modules": len(
                report["leaf_modules"]
            ),
            "hub_modules": len(
                report["hub_modules"]
            ),
            "isolated_modules": len(
                report["isolated_modules"]
            ),
        }

        return report


engine = ArchitectureAnalyzer()
