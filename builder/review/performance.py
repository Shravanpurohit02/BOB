import ast


class PerformanceAnalyzer:

    def analyze(
        self,
        source,
    ):

        tree = ast.parse(source)

        report = {
            "loops": 0,
            "nested_loops": 0,
            "comprehensions": 0,
            "issues": [],
            "score": 100,
        }

        for node in ast.walk(tree):

            if isinstance(
                node,
                (
                    ast.For,
                    ast.While,
                ),
            ):

                report["loops"] += 1

                for child in ast.walk(node):

                    if child is node:
                        continue

                    if isinstance(
                        child,
                        (
                            ast.For,
                            ast.While,
                        ),
                    ):
                        report["nested_loops"] += 1
                        report["issues"].append(
                            "Nested loop"
                        )
                        break

            elif isinstance(
                node,
                (
                    ast.ListComp,
                    ast.DictComp,
                    ast.SetComp,
                    ast.GeneratorExp,
                ),
            ):

                report["comprehensions"] += 1

        report["score"] -= (
            report["nested_loops"] * 20
        )

        if report["score"] < 0:
            report["score"] = 0

        return report

    def passed(
        self,
        report,
    ):

        return (
            report["nested_loops"] == 0
            and report["score"] >= 80
        )


engine = PerformanceAnalyzer()
