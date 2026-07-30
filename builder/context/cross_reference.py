class CrossReferenceEngine:

    def build(
        self,
        repository_graph,
        symbol_graph,
    ):

        references = {}

        for module, node in repository_graph.items():

            refs = set()

            refs.update(
                node.get(
                    "imports",
                    [],
                )
            )

            refs.update(
                node.get(
                    "imported_by",
                    [],
                )
            )

            for symbol in node.get(
                "references",
                [],
            ):

                refs.update(
                    symbol_graph["definitions"].get(
                        symbol,
                        [],
                    )
                )

            refs.discard(module)

            references[module] = sorted(refs)

        return references

    def related(
        self,
        references,
        module,
    ):

        return references.get(
            module,
            [],
        )

    def impact(
        self,
        references,
        modules,
    ):

        affected = set()

        stack = list(modules)

        while stack:

            current = stack.pop()

            if current in affected:
                continue

            affected.add(current)

            stack.extend(
                references.get(
                    current,
                    [],
                )
            )

        return sorted(affected)


engine = CrossReferenceEngine()
