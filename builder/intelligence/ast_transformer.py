import ast
import difflib
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class TransformResult:
    success: bool
    file: str
    diff: str
    message: str


class _ReplaceNode(ast.NodeTransformer):

    def __init__(self, target_type, target_name, replacement):
        self.target_type = target_type
        self.target_name = target_name
        self.replacement = replacement
        self.replaced = False

    def visit_ClassDef(self, node):
        if (
            self.target_type is ast.ClassDef
            and node.name == self.target_name
        ):
            self.replaced = True
            return self.replacement
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if (
            self.target_type is ast.FunctionDef
            and node.name == self.target_name
        ):
            self.replaced = True
            return self.replacement
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if (
            self.target_type is ast.AsyncFunctionDef
            and node.name == self.target_name
        ):
            self.replaced = True
            return self.replacement
        return self.generic_visit(node)


class ASTTransformer:

    def replace(
        self,
        file,
        symbol,
        replacement_source,
        write=False,
    ):

        path = Path(file)

        original = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(original)

        replacement_tree = ast.parse(
            replacement_source
        )

        replacement = replacement_tree.body[0]

        target = None

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
                    target = node
                    break

        if target is None:
            return TransformResult(
                False,
                str(path),
                "",
                "Target not found",
            )

        transformer = _ReplaceNode(
            type(target),
            symbol,
            replacement,
        )

        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)

        rebuilt = ast.unparse(new_tree)

        try:
            ast.parse(rebuilt)
        except Exception as e:
            return TransformResult(
                False,
                str(path),
                "",
                str(e),
            )

        diff = "\n".join(
            difflib.unified_diff(
                original.splitlines(),
                rebuilt.splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )

        if write:
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            try:
                path.write_text(
                    rebuilt,
                    encoding="utf-8",
                )
            except Exception:
                shutil.copy2(backup, path)
                raise

        return TransformResult(
            True,
            str(path),
            diff,
            "Transformed",
        )


ast_transformer = ASTTransformer()
