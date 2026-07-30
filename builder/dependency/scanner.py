import ast
from pathlib import Path

class DependencyScanner:

    def scan(self, workspace: str):

        imports = set()

        for file in Path(workspace).rglob("*.py"):

            try:
                tree = ast.parse(
                    file.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                )
            except Exception:
                continue

            for node in ast.walk(tree):

                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(
                            node.module.split(".")[0]
                        )

        return sorted(imports)

scanner = DependencyScanner()
