from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


@dataclass(slots=True)
class ReferenceSpan:
    file: str
    module: str
    symbol: str
    kind: str
    line: int
    column: int
    end_line: int
    end_column: int


@dataclass(slots=True)
class ReferenceIndex:
    references: list[ReferenceSpan] = field(default_factory=list)


class _Visitor(ast.NodeVisitor):
    def __init__(
        self,
        module: str,
        file: str,
        index: ReferenceIndex,
    ):
        self.module = module
        self.file = file
        self.index = index

    def _add(
        self,
        node,
        symbol: str,
        kind: str,
    ):
        self.index.references.append(
            ReferenceSpan(
                file=self.file,
                module=self.module,
                symbol=symbol,
                kind=kind,
                line=node.lineno,
                column=node.col_offset,
                end_line=getattr(node, "end_lineno", node.lineno),
                end_column=getattr(node, "end_col_offset", node.col_offset),
            )
        )

    def visit_Name(self, node):
        self._add(node, node.id, "name")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self._add(node, node.attr, "attribute")
        self.generic_visit(node)

    def visit_keyword(self, node):
        if node.arg:
            self._add(node, node.arg, "keyword")
        self.generic_visit(node)


class ReferenceSpanIndexer:

    SKIP: ClassVar[frozenset[str]] = frozenset({
        ".builder",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
    })

    def build(
        self,
        workspace: str,
    ) -> ReferenceIndex:

        root = Path(workspace)
        index = ReferenceIndex()

        for file in root.rglob("*.py"):

            if any(part in self.SKIP for part in file.parts):
                continue

            try:
                tree = ast.parse(
                    file.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                )
            except SyntaxError:
                continue

            module = ".".join(
                file.relative_to(root).with_suffix("").parts
            )

            _Visitor(
                module,
                str(file.relative_to(root)),
                index,
            ).visit(tree)

        return index


reference_span_indexer = ReferenceSpanIndexer()

__all__ = (
    "ReferenceIndex",
    "ReferenceSpan",
    "ReferenceSpanIndexer",
    "reference_span_indexer",
)
