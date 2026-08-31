from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder.intelligence.handlers.base import BaseHandler
from builder.intelligence.workspace_path import resolve_workspace_path

from builder.intelligence.handlers.models import (
    HandlerContext,
    HandlerResult,
    HandlerStatus,
)
from builder.intelligence.source_editor import source_editor
from builder.patch.engine import engine as patch_engine


@dataclass(slots=True)
class InsertSymbolRequest:
    file: str
    text: str
    offset: int = 0
    write: bool = False


class InsertSymbolHandler(BaseHandler):

    operation = "insert_symbol"

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):

            metadata = request.get("metadata", {})

            content = metadata.get("content")

            # Code-generation artifacts contain the complete resulting
            # file. For INSERT_SYMBOL the artifact adapter deliberately
            # maps action="modify" to this handler, so consume the
            # canonical generated content directly.
            if isinstance(content, str):
                request = InsertSymbolRequest(
                    file=request.get("file", ""),
                    text=content,
                    offset=0,
                    write=metadata.get("write", False),
                )
                replace_entire_file = True

            else:
                request = InsertSymbolRequest(
                    file=request.get("file", ""),
                    text=metadata.get("text", ""),
                    offset=metadata.get("offset", 0),
                    write=metadata.get("write", False),
                )
                replace_entire_file = False

        else:
            replace_entire_file = False

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

        if replace_entire_file:
            edit = source_editor.replace_range(
                source=before,
                start=0,
                end=len(before),
                replacement=request.text,
            )
        else:
            edit = source_editor.insert_before(
                source=before,
                offset=request.offset,
                text=request.text,
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

        diff = patch_engine.preview(patch)

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
                "Symbol inserted."
                if request.write
                else "Insertion prepared."
            ),
            patch_id=patch.id,
            diff=diff,
            metadata={
                "preview": not request.write,
                "offset": request.offset,
                "generated_content": replace_entire_file,
            },
        )


handler = InsertSymbolHandler()

__all__ = (
    "InsertSymbolHandler",
    "InsertSymbolRequest",
    "handler",
)
