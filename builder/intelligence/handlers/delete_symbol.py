from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder.intelligence.ast_editor import ast_editor
from builder.intelligence.handlers.base import BaseHandler
from builder.intelligence.workspace_path import resolve_workspace_path

from builder.intelligence.handlers.models import (
    HandlerContext,
    HandlerResult,
    HandlerStatus,
)
from builder.patch.engine import engine as patch_engine


@dataclass(slots=True)
class DeleteSymbolRequest:
    file: str
    symbol: str
    write: bool = False


class DeleteSymbolHandler(BaseHandler):
    operation = "delete_symbol"

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

    @staticmethod
    def _remove_location(
        source: str,
        location,
    ) -> str:
        lines = source.splitlines(
            keepends=True,
        )

        start = location.start - 1
        end = location.end

        return "".join(
            lines[:start]
            + lines[end:]
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

            symbol = metadata.get(
                "symbol",
                "",
            )

            qualified = metadata.get(
                "qualified_name",
                "",
            )

            if symbols:
                resolved = symbols[0]

                resolved_name, resolved_qualified = (
                    self._symbol_info(resolved)
                )

                if not symbol:
                    symbol = resolved_name

                if not qualified:
                    qualified = resolved_qualified

            request = DeleteSymbolRequest(
                file=file,
                symbol=str(symbol),
                write=bool(
                    metadata.get(
                        "write",
                        False,
                    )
                ),
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

        symbol_name = str(
            request.symbol
        ).strip()

        if not symbol_name:
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(path),
                message="Symbol name is empty.",
            )

        qualified = ""

        if isinstance(request, DeleteSymbolRequest):
            qualified = ""

        module = self._module_for_file(
            context.workspace,
            request.file,
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

        location = locations[0]

        old = self._extract_location(
            before,
            location,
        )

        updated = self._remove_location(
            before,
            location,
        )

        if old == updated:
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(path),
                message=(
                    "Symbol deletion produced "
                    "no source change."
                ),
            )

        patch = patch_engine.create(
            path=str(path),
            updated=updated,
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
                "Symbol deleted."
                if request.write
                else "Deletion prepared."
            ),
            patch_id=patch.id,
            diff=diff,
            metadata={
                "preview": not request.write,
                "deleted_symbol": symbol_name,
                "qualified_name": qualified,
                "deleted_source": old,
            },
        )


handler = DeleteSymbolHandler()

__all__ = (
    "DeleteSymbolHandler",
    "DeleteSymbolRequest",
    "handler",
)
