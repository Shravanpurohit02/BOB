import ast
from pathlib import Path


class DependencyMap:

    def build(
        self,
        workspace: str,
    ):

        graph = {}

        root = Path(workspace)

        for file in root.rglob("*.py"):

            module = ".".join(
                file.relative_to(root).with_suffix("").parts
            )

            graph[module] = set()

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
                        graph[module].add(alias.name)

                elif isinstance(node, ast.ImportFrom):

                    if node.module:
                        graph[module].add(node.module)

        return {
            k: sorted(v)
            for k, v in graph.items()
        }


dependency_map = DependencyMap()
