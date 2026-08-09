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
class CreateFileRequest:
    file: str
    content: str = ""
    write: bool = False


class CreateFileHandler(BaseHandler):

    operation = "create_file"

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):

            metadata = request.get("metadata", {})

            request = CreateFileRequest(
                file=request.get("file", ""),
                content=metadata.get("content", ""),
                write=metadata.get("write", False),
            )

        path = resolve_workspace_path(
            context.workspace,
            request.file,
        )

        if path.exists():
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(path),
                message="File already exists.",
            )

        if not request.write:
            return HandlerResult(
                success=True,
                status=HandlerStatus.SUCCESS,
                operation=self.operation,
                file=str(path),
                message="Create operation prepared.",
                metadata={
                    "preview": True,
                    "content_length": len(request.content),
                },
            )

        try:
            patch = patch_engine.create(
                path=str(path),
                updated=request.content,
                action="create",
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
            message="File created.",
            patch_id=patch.id,
            diff=diff,
            metadata={
                "preview": False,
                "created": True,
                "content_length": len(request.content),
            },
        )


handler = CreateFileHandler()

__all__ = (
    "CreateFileHandler",
    "CreateFileRequest",
    "handler",
)
