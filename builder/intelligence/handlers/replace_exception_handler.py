from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder.intelligence.handlers.base import BaseHandler
from builder.intelligence.handlers.models import HandlerResult, HandlerStatus
from builder.intelligence.source_editor import source_editor
from builder.intelligence.transactional_patch import transactional_patch_engine


@dataclass(slots=True)
class ReplaceExceptionHandlerRequest:
    file: str
    old: str = "except Exception:"
    new: str = "except (KeyboardInterrupt, SystemExit):\n            raise\n\n        except Exception:  # noqa: BLE001"
    write: bool = False


class ReplaceExceptionHandler(BaseHandler):
    operation = "replace_exception_handler"

    def _execute(self, request, context) -> HandlerResult:
        if isinstance(request, dict):
            metadata = request.get("metadata", {})
            request = ReplaceExceptionHandlerRequest(
                file=request["file"],
                old=metadata.get("old", "except Exception:"),
                new=metadata.get("new", ReplaceExceptionHandlerRequest.new),
                write=metadata.get("write", False),
            )

        path = Path(request.file)
        if not path.exists():
            return HandlerResult(False, HandlerStatus.FAILED, self.operation, request.file, message="File not found.")

        before = path.read_text(encoding="utf-8", errors="ignore")

        edit = source_editor.replace_text(before, request.old, request.new, count=1)

        if not edit.success:
            return HandlerResult(False, HandlerStatus.FAILED, self.operation, request.file, message=edit.message)

        commit = transactional_patch_engine.commit_source(
            file=request.file,
            before=before,
            updated=edit.after,
            write=request.write,
            transaction=context.transaction,
        )

        return HandlerResult(
            success=commit.success,
            status=HandlerStatus.SUCCESS if commit.success else HandlerStatus.FAILED,
            operation=self.operation,
            file=request.file,
            message=commit.message,
            diff=commit.diff,
            patch_id=commit.backup,
            metadata={"replacement": "BLE001"},
        )


handler = ReplaceExceptionHandler()

__all__ = (
    "ReplaceExceptionHandler",
    "ReplaceExceptionHandlerRequest",
    "handler",
)
