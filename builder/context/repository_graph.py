class RepositoryGraph:

    def build(
        self,
        modules,
        imports,
        symbols,
    ):

        graph = {}

        for module in modules:

            graph[module.path] = {
                "imports": imports["imports"].get(
                    module.path,
                    [],
                ),
                "imported_by": imports["reverse"].get(
                    module.path,
                    [],
                ),
                "exports": symbols["exports"].get(
                    module.path,
                    [],
                ),
                "references": symbols["references"].get(
                    module.path,
                    [],
                ),
            }

        return graph

    def neighbours(
        self,
        graph,
        module,
    ):

        node = graph.get(
            module,
            {},
        )

        return sorted(
            set(
                node.get("imports", [])
                +
                node.get("imported_by", [])
            )
        )

    def degree(
        self,
        graph,
        module,
    ):

        node = graph.get(
            module,
            {},
        )

        return (
            len(node.get("imports", []))
            +
            len(node.get("imported_by", []))
        )


engine = RepositoryGraph()
