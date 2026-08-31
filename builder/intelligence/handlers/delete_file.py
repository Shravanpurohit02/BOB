from __future__ import annotations

from dataclasses import dataclass

from builder.intelligence.handlers.base import BaseHandler
from builder.intelligence.handlers.models import (
    HandlerContext,
    HandlerResult,
    HandlerStatus,
)
from builder.intelligence.workspace_path import resolve_workspace_path
from builder.patch.engine import engine as patch_engine


@dataclass(slots=True)
class DeleteFileRequest:
    file: str
    write: bool = False


class DeleteFileHandler(BaseHandler):

    operation = "delete_file"

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):

            metadata = request.get("metadata", {})

            request = DeleteFileRequest(
                file=request.get("file", ""),
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
                message="File does not exist.",
            )

        if not path.is_file():
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(path),
                message="Target is not a file.",
            )

        if not request.write:
            return HandlerResult(
                success=True,
                status=HandlerStatus.SUCCESS,
                operation=self.operation,
                file=str(path),
                message="Delete operation prepared.",
                metadata={
                    "preview": True,
                },
            )

        try:
            patch = patch_engine.create(
                path=str(path),
                updated="",
                action="delete",
            )

            diff = patch_engine.preview(patch)

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
            message="File deleted.",
            patch_id=patch.id,
            diff=diff,
            metadata={
                "preview": False,
                "deleted": True,
                "original_length": len(patch.original),
            },
        )


handler = DeleteFileHandler()

__all__ = (
    "DeleteFileHandler",
    "DeleteFileRequest",
    "handler",
)
