import ast


class RefactoringAdvisor:

    def analyze(
        self,
        source,
    ):

        tree = ast.parse(source)

        suggestions = []

        for node in ast.walk(tree):

            if isinstance(
                node,
                ast.FunctionDef,
            ):

                if len(node.body) > 20:

                    suggestions.append(
                        {
                            "type":"extract-method",
                            "target":node.name,
                        }
                    )

            elif isinstance(
                node,
                ast.ClassDef,
            ):

                methods = [
                    n
                    for n in node.body
                    if isinstance(
                        n,
                        ast.FunctionDef,
                    )
                ]

                if len(methods) > 10:

                    suggestions.append(
                        {
                            "type":"split-class",
                            "target":node.name,
                        }
                    )

        return {
            "suggestions":suggestions,
            "count":len(suggestions),
        }

    def priority(
        self,
        report,
    ):

        if report["count"] >= 5:
            return "high"

        if report["count"] >= 2:
            return "medium"

        return "low"


engine = RefactoringAdvisor()
