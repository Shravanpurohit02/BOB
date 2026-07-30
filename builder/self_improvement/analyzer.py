import ast
from pathlib import Path


class Analyzer:

    EXCLUDED = {
        "__pycache__",
        ".git",
        ".builder/output",
        ".builder/backups",
        ".venv",
        "venv",
        "node_modules",
        "backend/tests",
        "backend/migrations",
    }

    def _excluded(self, path: Path):

        text = path.as_posix()

        return any(
            text.startswith(item)
            or f"/{item}/" in text
            for item in self.EXCLUDED
        )

    def analyze(
        self,
        workspace: str,
    ):

        issues = []

        root = Path(workspace)

        for path in root.rglob("*.py"):

            if self._excluded(path.relative_to(root)):
                continue

            try:

                source = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

            except Exception:
                continue

            if "TODO" in source:
                issues.append(
                    (
                        str(path),
                        "TODO found",
                    )
                )

            try:

                tree = ast.parse(source)

                for node in ast.walk(tree):

                    if (
                        isinstance(node, ast.Pass)
                    ):
                        issues.append(
                            (
                                str(path),
                                "Pass statement found",
                            )
                        )
                        break

            except Exception:
                issues.append(
                    (
                        str(path),
                        "Python parse failure",
                    )
                )

        return issues


analyzer = Analyzer()
