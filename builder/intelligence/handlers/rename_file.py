from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder.intelligence.handlers.base import (
    BaseHandler,
)
from builder.intelligence.handlers.models import (
    HandlerResult,
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
        context,
    ) -> HandlerResult:

        if isinstance(request, dict):
            metadata = request.get(
                "metadata",
                {},
            )

            request = RenameFileRequest(
                source=request["file"],
                destination=metadata.get(
                    "destination",
                    "",
                ),
                write=metadata.get(
                    "write",
                    False,
                ),
            )

        source = Path(request.source)
        destination = Path(request.destination)

        if not source.exists():
            return HandlerResult(
                success=False,
                message="Source file does not exist.",
            )

        if not request.destination:
            return HandlerResult(
                success=False,
                message="Destination path not supplied.",
            )

        if destination.exists():
            return HandlerResult(
                success=False,
                message="Destination already exists.",
            )

        if request.write:

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            source.rename(
                destination,
            )

            return HandlerResult(
                success=True,
                message="File renamed.",
                metadata={
                    "source": str(source),
                    "destination": str(destination),
                },
            )

        return HandlerResult(
            success=True,
            message="Rename operation prepared.",
            metadata={
                "source": str(source),
                "destination": str(destination),
            },
        )


handler = RenameFileHandler()

__all__ = (
    "RenameFileHandler",
    "RenameFileRequest",
    "handler",
)
