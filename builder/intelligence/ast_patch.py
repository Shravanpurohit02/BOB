import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PatchResult:
    success: bool
    file: str
    symbol: str
    before: str
    after: str
    message: str


class ASTPatchEngine:

    def _find_node(self, tree, symbol):

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                if node.name == symbol:
                    return node

        return None

    def replace(self, file, symbol, new_source):

        path = Path(file)

        source = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(source)

        node = self._find_node(tree, symbol)

        if node is None:
            return PatchResult(
                False,
                str(path),
                symbol,
                "",
                "",
                "Symbol not found",
            )

        lines = source.splitlines()

        start = node.lineno - 1
        end = node.end_lineno

        before = "\n".join(lines[start:end])

        replacement = new_source.strip("\n").splitlines()

        updated = (
            lines[:start]
            + replacement
            + lines[end:]
        )

        after = "\n".join(updated)

        try:
            ast.parse(after)
        except Exception as e:
            return PatchResult(
                False,
                str(path),
                symbol,
                before,
                "",
                str(e),
            )

        return PatchResult(
            True,
            str(path),
            symbol,
            before,
            after,
            "Validated",
        )


ast_patch_engine = ASTPatchEngine()
