import ast


class SecurityAnalyzer:

    DANGEROUS = {
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    def analyze(
        self,
        source,
    ):

        tree = ast.parse(source)

        report = {
            "issues": [],
            "score": 100,
        }

        for node in ast.walk(tree):

            if isinstance(
                node,
                ast.Call,
            ):

                if isinstance(
                    node.func,
                    ast.Name,
                ):

                    name = node.func.id

                    if name in self.DANGEROUS:

                        report["issues"].append(
                            {
                                "severity":"high",
                                "type":"dangerous-call",
                                "symbol":name,
                            }
                        )

            elif isinstance(
                node,
                ast.Global,
            ):

                report["issues"].append(
                    {
                        "severity":"medium",
                        "type":"global-statement",
                    }
                )

        report["score"] -= (
            len(report["issues"]) * 20
        )

        if report["score"] < 0:
            report["score"] = 0

        return report

    def passed(
        self,
        report,
    ):

        return (
            report["score"] >= 80
            and not any(
                issue["severity"] == "high"
                for issue in report["issues"]
            )
        )


engine = SecurityAnalyzer()
