from __future__ import annotations

from dataclasses import dataclass

from builder.intelligence.handlers.base import BaseHandler
from builder.intelligence.handlers.models import (
    HandlerContext,
    HandlerResult,
)
from builder.intelligence.handlers.replace_symbol import (
    ReplaceSymbolRequest,
    handler as replace_symbol_handler,
)


@dataclass(slots=True)
class RenameSymbolRequest:
    file: str
    old_name: str
    new_name: str
    write: bool = False


class RenameSymbolHandler(BaseHandler):

    operation = "rename_symbol"

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):

            metadata = request.get("metadata", {})

            request = RenameSymbolRequest(
                file=request.get("file", ""),
                old_name=metadata.get("old_name", ""),
                new_name=metadata.get("new_name", ""),
                write=metadata.get("write", False),
            )

        replace_request = ReplaceSymbolRequest(
            file=request.file,
            old=request.old_name,
            new=request.new_name,
            write=request.write,
        )

        result = replace_symbol_handler.execute(
            replace_request,
            context,
        )

        result.operation = self.operation

        return result


handler = RenameSymbolHandler()

__all__ = (
    "RenameSymbolHandler",
    "RenameSymbolRequest",
    "handler",
)
