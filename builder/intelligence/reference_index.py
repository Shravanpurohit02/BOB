import ast
from pathlib import Path

from .references import (
    Definition,
    Reference,
    ReferenceIndex,
)


class _Visitor(ast.NodeVisitor):

    def __init__(self, module: str, index: ReferenceIndex):
        self.module = module
        self.index = index

    def _add_definition(self, name, kind, line):
        d = Definition(name, self.module, kind, line)
        self.index.definitions.append(d)
        self.index.definitions_by_name.setdefault(name, []).append(d)

    def _add_reference(self, name, kind, line):
        r = Reference(name, self.module, kind, line)
        self.index.references.append(r)
        self.index.references_by_name.setdefault(name, []).append(r)

    def visit_FunctionDef(self, node):
        self._add_definition(node.name, "function", node.lineno)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._add_definition(node.name, "async_function", node.lineno)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self._add_definition(node.name, "class", node.lineno)
        self.generic_visit(node)

    def visit_Name(self, node):
        self._add_reference(node.id, "name", node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self._add_reference(node.attr, "attribute", node.lineno)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self._add_reference(alias.name, "import", node.lineno)

    def visit_ImportFrom(self, node):
        if node.module:
            self._add_reference(node.module, "importfrom", node.lineno)
        for alias in node.names:
            self._add_reference(alias.name, "importfrom", node.lineno)


class ReferenceIndexer:

    def build(self, workspace: str):

        root = Path(workspace)
        index = ReferenceIndex()

        SKIP_DIRS = {
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

            if any(part in SKIP_DIRS for part in file.parts):
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


reference_indexer = ReferenceIndexer()
