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


@dataclass(slots=True)
class RenameFileRequest:
    source: str
    destination: str
    write: bool = False


class RenameFileHandler(BaseHandler):

    operation = "rename_file"

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):

            metadata = request.get("metadata", {})

            request = RenameFileRequest(
                source=request.get("file", ""),
                destination=metadata.get("destination", ""),
                write=metadata.get("write", False),
            )

        source = resolve_workspace_path(
            context.workspace,
            request.source,
        )

        destination = resolve_workspace_path(
            context.workspace,
            request.destination,
        )

        if not source.exists():
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(source),
                message="Source file does not exist.",
            )

        if not request.destination:
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(source),
                message="Destination path not supplied.",
            )

        if destination.exists():
            return HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=str(source),
                message="Destination already exists.",
            )

        if request.write:

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            source.rename(destination)

            return HandlerResult(
                success=True,
                status=HandlerStatus.SUCCESS,
                operation=self.operation,
                file=str(destination),
                message="File renamed.",
                metadata={
                    "source": str(source),
                    "destination": str(destination),
                },
            )

        return HandlerResult(
            success=True,
            status=HandlerStatus.SUCCESS,
            operation=self.operation,
            file=str(source),
            message="Rename operation prepared.",
            metadata={
                "source": str(source),
                "destination": str(destination),
                "preview": True,
            },
        )


handler = RenameFileHandler()

__all__ = (
    "RenameFileHandler",
    "RenameFileRequest",
    "handler",
)
