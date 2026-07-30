from builder.context.semantic_search import engine as semantic


class HybridRetrieval:

    def retrieve(
        self,
        modules,
        dependency_graph,
        query,
        limit=20,
    ):

        ranked = semantic.search(
            modules,
            query,
            limit * 2,
        )

        scores = {}

        for module in ranked:

            score = 100

            score += (
                len(
                    dependency_graph["reverse"].get(
                        module.path,
                        [],
                    )
                )
                * 5
            )

            score += dependency_graph["depth"].get(
                module.path,
                0,
            )

            scores[module.path] = score

        ranked.sort(
            key=lambda m: scores[m.path],
            reverse=True,
        )

        return ranked[:limit]


engine = HybridRetrieval()
