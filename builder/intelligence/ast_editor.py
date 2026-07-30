import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class EditLocation:
    file: str
    module: str
    cls: str | None
    symbol: str
    start: int
    end: int


class _Visitor(ast.NodeVisitor):

    def __init__(self, module, relpath):
        self.module = module
        self.relpath = relpath
        self.class_stack = []
        self.locations = []

    def visit_ClassDef(self, node):
        self.locations.append(
            EditLocation(
                file=self.relpath,
                module=self.module,
                cls=".".join(self.class_stack) if self.class_stack else None,
                symbol=node.name,
                start=node.lineno,
                end=getattr(node, "end_lineno", node.lineno),
            )
        )

        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        self.locations.append(
            EditLocation(
                file=self.relpath,
                module=self.module,
                cls=".".join(self.class_stack) if self.class_stack else None,
                symbol=node.name,
                start=node.lineno,
                end=getattr(node, "end_lineno", node.lineno),
            )
        )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


class ASTEditor:

    def build(self, workspace):

        root = Path(workspace)
        self.locations = []

        SKIP = {
            ".builder",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            "build",
            "dist",
        }

        for file in root.rglob("*.py"):

            if any(p in SKIP for p in file.parts):
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
                file.relative_to(root).with_suffix("").parts
            )

            visitor = _Visitor(module, str(file.relative_to(root)))
            visitor.visit(tree)

            self.locations.extend(visitor.locations)

    def find_symbol(self, qualified):

        parts = qualified.split(".")
        symbol = parts[-1]

        cls = None
        module = None

        if len(parts) >= 2:
            cls = parts[-2]

        if len(parts) >= 3:
            module = ".".join(parts[:-2])

        matches = []

        for loc in self.locations:

            if loc.symbol != symbol:
                continue

            if cls and (loc.cls or "").split(".")[-1] != cls:
                continue

            if module and loc.module != module:
                continue

            matches.append(loc)

        return matches


ast_editor = ASTEditor()
