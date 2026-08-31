from __future__ import annotations

from dataclasses import dataclass

from builder.intelligence.ast_editor import ASTEditor, ast_editor
from builder.intelligence.handlers.base import BaseHandler
from builder.intelligence.handlers.models import (
    HandlerContext,
    HandlerResult,
    HandlerStatus,
)
from builder.intelligence.workspace_path import resolve_workspace_path
from builder.intelligence.source_editor import source_editor
from builder.patch.engine import engine as patch_engine


@dataclass(slots=True)
class ReplaceSymbolRequest:
    file: str
    old: str
    new: str
    write: bool = False


class ReplaceSymbolHandler(BaseHandler):

    operation = "replace_symbol"

    @staticmethod
    def _symbol_info(symbol):
        if isinstance(symbol, str):
            return symbol, ""

        if isinstance(symbol, dict):
            return (
                symbol.get("name")
                or symbol.get("symbol")
                or "",
                symbol.get("qualified_name")
                or symbol.get("id")
                or "",
            )

        return (
            getattr(symbol, "name", ""),
            getattr(symbol, "qualified_name", "")
            or getattr(symbol, "id", ""),
        )

    @staticmethod
    def _module_for_file(
        workspace: str,
        file: str,
    ) -> str:
        from pathlib import Path

        root = Path(workspace).resolve()
        path = resolve_workspace_path(
            workspace,
            file,
        )

        relative = path.relative_to(root)

        return ".".join(
            relative.with_suffix("").parts
        )

    @staticmethod
    def _extract_location(
        source: str,
        location,
    ) -> str:
        lines = source.splitlines(
            keepends=True,
        )

        return "".join(
            lines[
                location.start - 1:
                location.end
            ]
        )

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):
            metadata = request.get(
                "metadata",
                {},
            )

            file = str(
                request.get(
                    "file",
                    "",
                )
            )

            symbols = request.get(
                "symbols",
                [],
            )

            content = metadata.get(
                "content",
                "",
            )

            old = metadata.get(
                "old",
                "",
            )

            new = metadata.get(
                "new",
                "",
            )

            write = bool(
                metadata.get(
                    "write",
                    False,
                )
            )

            path = resolve_workspace_path(
                context.workspace,
                file,
            )

            if not path.exists():
                return HandlerResult(
                    success=False,
                    status=HandlerStatus.FAILED,
                    operation=self.operation,
                    file=str(path),
                    message="File not found.",
                )

            before = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            if content and symbols:
                symbol_name, qualified = (
                    self._symbol_info(
                        symbols[0]
                    )
                )

                if not qualified:
                    module = self._module_for_file(
                        context.workspace,
                        file,
                    )

                    qualified = (
                        f"{module}.{symbol_name}"
                    )

                ast_editor.build(
                    context.workspace
                )

                locations = ast_editor.find_symbol(
                    qualified
                )

                if not locations:
                    return HandlerResult(
                        success=False,
                        status=HandlerStatus.FAILED,
                        operation=self.operation,
                        file=str(path),
                        message=(
                            "Resolved symbol location "
                            f"not found: {qualified}"
                        ),
                    )

                old = self._extract_location(
                    before,
                    locations[0],
                )

                generated_editor = ASTEditor()

                # Parse generated content directly rather than
                # modifying the workspace with a temporary file.
                import ast

                try:
                    tree = ast.parse(content)
                except SyntaxError as exc:
                    return HandlerResult(
                        success=False,
                        status=HandlerStatus.FAILED,
                        operation=self.operation,
                        file=str(path),
                        message=(
                            "Generated content is not valid "
                            f"Python: {exc}"
                        ),
                    )

                generated_locations = []

                class Visitor(ast.NodeVisitor):
                    def visit_ClassDef(self, node):
                        if node.name == symbol_name:
                            generated_locations.append(
                                (
                                    node.lineno,
                                    getattr(
                                        node,
                                        "end_lineno",
                                        node.lineno,
                                    ),
                                )
                            )
                        self.generic_visit(node)

                    def visit_FunctionDef(self, node):
                        if node.name == symbol_name:
                            generated_locations.append(
                                (
                                    node.lineno,
                                    getattr(
                                        node,
                                        "end_lineno",
                                        node.lineno,
                                    ),
                                )
                            )
                        self.generic_visit(node)

                    visit_AsyncFunctionDef = visit_FunctionDef

                Visitor().visit(tree)

                if not generated_locations:
                    return HandlerResult(
                        success=False,
                        status=HandlerStatus.FAILED,
                        operation=self.operation,
                        file=str(path),
                        message=(
                            "Generated content does not contain "
                            f"symbol: {symbol_name}"
                        ),
                    )

                start, end = generated_locations[0]

                generated_lines = content.splitlines(
                    keepends=True,
                )

                new = "".join(
                    generated_lines[
                        start - 1:
                        end
                    ]
                )

            request = ReplaceSymbolRequest(
                file=file,
                old=old,
                new=new,
                write=write,
            )

        path = resolve_workspace_path(
            context.workspace,
            request.file,
        )

        if not path.exists():
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(path),
                message="File not found.",
            )

        before = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        edit = source_editor.replace_text(
            source=before,
            old=request.old,
            new=request.new,
            count=1,
        )

        if not edit.success:
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(path),
                message=edit.message,
            )

        patch = patch_engine.create(
            path=str(path),
            updated=edit.after,
        )

        diff = patch_engine.preview(
            patch
        )

        if request.write:
            patch_engine.commit(
                patch,
                transaction=context.transaction,
            )

        return HandlerResult(
            success=True,
            status=HandlerStatus.SUCCESS,
            operation=self.operation,
            file=str(path),
            message=(
                "Symbol replaced."
                if request.write
                else "Replacement prepared."
            ),
            patch_id=patch.id,
            diff=diff,
            metadata={
                "preview": not request.write,
                "old": request.old,
                "new": request.new,
            },
        )


handler = ReplaceSymbolHandler()

__all__ = (
    "ReplaceSymbolHandler",
    "ReplaceSymbolRequest",
    "handler",
)
