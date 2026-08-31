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
class ReplaceExceptionHandlerRequest:
    file: str
    old: str = "except Exception:"
    new: str = (
        "except (KeyboardInterrupt, SystemExit):\n"
        "            raise\n\n"
        "        except Exception:  # noqa: BLE001"
    )
    write: bool = False


class ReplaceExceptionHandler(BaseHandler):

    operation = "replace_exception_handler"

    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        if isinstance(request, dict):
            metadata = request.get("metadata", {})
            request = ReplaceExceptionHandlerRequest(
                file=request.get("file", ""),
                old=metadata.get("old", "except Exception:"),
                new=metadata.get(
                    "new",
                    ReplaceExceptionHandlerRequest.new,
                ),
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
                file=request.file,
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
                file=request.file,
                message=edit.message,
            )

        patch = patch_engine.create(
            path=request.file,
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
            file=request.file,
            message="Exception handler replaced."
            if request.write
            else "Preview generated.",
            patch_id=patch.id,
            diff=diff,
            metadata={
                "preview": not request.write,
            },
        )


handler = ReplaceExceptionHandler()

__all__ = (
    "ReplaceExceptionHandler",
    "ReplaceExceptionHandlerRequest",
    "handler",
)
