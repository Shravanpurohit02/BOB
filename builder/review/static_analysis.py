import ast


class StaticAnalysisEngine:

    def analyze(
        self,
        source,
    ):

        tree = ast.parse(source)

        report = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "assignments": 0,
            "returns": 0,
        }

        for node in ast.walk(tree):

            if isinstance(
                node,
                ast.FunctionDef,
            ):
                report["functions"] += 1

            elif isinstance(
                node,
                ast.ClassDef,
            ):
                report["classes"] += 1

            elif isinstance(
                node,
                (
                    ast.Import,
                    ast.ImportFrom,
                ),
            ):
                report["imports"] += 1

            elif isinstance(
                node,
                ast.Assign,
            ):
                report["assignments"] += 1

            elif isinstance(
                node,
                ast.Return,
            ):
                report["returns"] += 1

        return report

    def score(
        self,
        report,
    ):

        return (
            report["functions"]
            + report["classes"]
            + report["imports"]
        )


engine = StaticAnalysisEngine()
