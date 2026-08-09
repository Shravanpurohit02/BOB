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
from builder.patch.engine import engine as patch_engine


@dataclass(slots=True)
class ModifyFileRequest:
    file: str
    content: str = ""
    write: bool = False


class ModifyFileHandler(BaseHandler):

    operation = "modify_file"

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):

            metadata = request.get("metadata", {})

            request = ModifyFileRequest(
                file=request.get("file", ""),
                content=metadata.get("content", ""),
                write=metadata.get("write", False),
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

        if not path.is_file():
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(path),
                message="Target is not a file.",
            )

        before = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        patch = patch_engine.create(
            path=str(path),
            updated=request.content,
            action="modify",
        )

        diff = patch_engine.preview(patch)

        if request.write:
            try:
                patch_engine.commit(
                    patch,
                    transaction=context.transaction,
                )
            except Exception as exc:
                return HandlerResult(
                    success=False,
                    status=HandlerStatus.FAILED,
                    operation=self.operation,
                    file=str(path),
                    message=str(exc),
                    error=type(exc).__name__,
                )

        return HandlerResult(
            success=True,
            status=HandlerStatus.SUCCESS,
            operation=self.operation,
            file=str(path),
            message=(
                "File modified."
                if request.write
                else "Modification prepared."
            ),
            patch_id=patch.id,
            diff=diff,
            metadata={
                "preview": not request.write,
                "old_length": len(before),
                "new_length": len(request.content),
            },
        )


handler = ModifyFileHandler()

__all__ = (
    "ModifyFileHandler",
    "ModifyFileRequest",
    "handler",
)
