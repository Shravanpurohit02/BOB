import ast


class CodeQualityAnalyzer:

    def analyze(
        self,
        source,
    ):

        tree = ast.parse(source)

        report = {
            "functions": 0,
            "classes": 0,
            "long_functions": 0,
            "nested_blocks": 0,
            "issues": [],
        }

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):

                report["functions"] += 1

                body = len(node.body)

                if body > 20:
                    report["long_functions"] += 1
                    report["issues"].append(
                        f"Long function: {node.name}"
                    )

            elif isinstance(node, ast.ClassDef):

                report["classes"] += 1

            elif isinstance(
                node,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                ),
            ):

                depth = len(getattr(node, "body", []))

                if depth > 5:
                    report["nested_blocks"] += 1

        report["score"] = max(
            0,
            100
            - report["long_functions"] * 10
            - report["nested_blocks"] * 5
        )

        return report

    def passed(
        self,
        report,
    ):

        return (
            report["score"] >= 80
            and report["long_functions"] == 0
        )


engine = CodeQualityAnalyzer()
