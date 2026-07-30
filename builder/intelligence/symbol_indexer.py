import ast
from pathlib import Path

from .symbols import (
    Symbol,
    SymbolIndex,
)


class SymbolIndexer:

    EXCLUDED = {
        ".git",
        ".builder",
        "builder_backup",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
        "reports",
        "downloads",
        "temp",
    }

    def _excluded(
        self,
        path: Path,
    ):

        parts = set(path.parts)

        return bool(
            parts & self.EXCLUDED
        )

    def build(
        self,
        workspace: str,
    ):

        index = SymbolIndex()

        root = Path(workspace)

        for file in root.rglob("*.py"):

            relative = file.relative_to(root)

            if self._excluded(relative):
                continue

            try:

                tree = ast.parse(
                    file.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                )

            except Exception:
                continue

            module = ".".join(
                relative.with_suffix("").parts
            )

            index.modules[module] = str(file)

            for node in ast.walk(tree):

                if not isinstance(
                    node,
                    (
                        ast.ClassDef,
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                ):
                    continue

                kind = (
                    type(node)
                    .__name__
                    .replace("Def", "")
                    .lower()
                )

                index.symbols.append(
                    Symbol(
                        name=node.name,
                        kind=kind,
                        module=module,
                        line=node.lineno,
                    )
                )

        return index


indexer = SymbolIndexer()
