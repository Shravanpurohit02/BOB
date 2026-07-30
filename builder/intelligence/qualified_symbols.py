import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class QualifiedSymbol:
    id: str
    name: str
    module: str
    cls: str | None
    kind: str
    line: int


@dataclass(slots=True)
class QualifiedSymbolIndex:
    symbols: list[QualifiedSymbol] = field(default_factory=list)
    by_id: dict[str, QualifiedSymbol] = field(default_factory=dict)
    by_name: dict[str, list[QualifiedSymbol]] = field(default_factory=dict)


class _Visitor(ast.NodeVisitor):

    def __init__(self, module, index):
        self.module = module
        self.index = index
        self.class_stack = []

    def _add(self, node, kind):

        cls = ".".join(self.class_stack) if self.class_stack else None

        if cls:
            sid = f"{self.module}.{cls}.{node.name}"
        else:
            sid = f"{self.module}.{node.name}"

        sym = QualifiedSymbol(
            id=sid,
            name=node.name,
            module=self.module,
            cls=cls,
            kind=kind,
            line=node.lineno,
        )

        self.index.symbols.append(sym)
        self.index.by_id[sid] = sym
        self.index.by_name.setdefault(node.name, []).append(sym)

    def visit_ClassDef(self, node):
        self._add(node, "class")
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        self._add(node, "function")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


class QualifiedSymbolIndexer:

    def build(self, workspace):

        root = Path(workspace)
        index = QualifiedSymbolIndex()

        SKIP = {
            ".builder",
            "builder_backup",
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "build",
            "dist",
            ".pytest_cache",
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

            _Visitor(module, index).visit(tree)

        return index


qualified_symbol_indexer = QualifiedSymbolIndexer()
