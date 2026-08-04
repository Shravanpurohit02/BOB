from __future__ import annotations

import ast
import difflib
from dataclasses import dataclass
from pathlib import Path

from builder.intelligence.source_editor import source_editor
from builder.intelligence.source_span import source_span_resolver


@dataclass(slots=True)
class RenameResult:
    success: bool
    file: str
    before: str
    after: str
    diff: str
    message: str


class ASTRenameEngine:
    """Minimal source-preserving rename engine for declarations."""

    @staticmethod
    def _find_target(tree: ast.AST, old_name: str):
        for node in ast.walk(tree):
            if (
                isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef,
                    ),
                )
                and node.name == old_name
            ):
                return node
        return None

    def rename(self, file: str, old_name: str, new_name: str) -> RenameResult:
        path = Path(file)

        if not path.exists():
            return RenameResult(False, file, "", "", "", "File not found.")

        before = path.read_text(encoding="utf-8", errors="ignore")

        try:
            tree = ast.parse(before)
        except SyntaxError as exc:
            return RenameResult(False, file, before, "", "", str(exc))

        target = self._find_target(tree, old_name)
        if target is None:
            return RenameResult(False, file, before, before, "", "Target not found.")

        try:
            span = source_span_resolver.identifier_span(
                before,
                target.lineno,
                old_name,
            )
        except ValueError as exc:
            return RenameResult(False, file, before, before, "", str(exc))

        edit = source_editor.rename_identifier(
            source=before,
            start=span.start,
            end=span.end,
            new_name=new_name,
        )

        if not edit.success:
            return RenameResult(False, file, before, before, "", edit.message)

        after = edit.after

        try:
            ast.parse(after)
        except SyntaxError as exc:
            return RenameResult(False, file, before, "", "", str(exc))

        diff = "\n".join(
            difflib.unified_diff(
                before.splitlines(),
                after.splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )

        return RenameResult(True, file, before, after, diff, "Renamed")


ast_rename_engine = ASTRenameEngine()

__all__ = (
    "ASTRenameEngine",
    "RenameResult",
    "ast_rename_engine",
)
