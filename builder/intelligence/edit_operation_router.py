from dataclasses import dataclass
from enum import Enum

from .operation_planner import OperationType


class DispatchStatus(str, Enum):
    READY = "ready"
    DISPATCHED = "dispatched"
    UNSUPPORTED = "unsupported"


@dataclass(slots=True)
class DispatchResult:
    success: bool
    status: DispatchStatus
    handler: str
    message: str = ""


class EditOperationRouter:

    HANDLERS = {
        OperationType.REPLACE_SYMBOL: "replace_symbol",
        OperationType.INSERT_SYMBOL: "insert_symbol",
        OperationType.DELETE_SYMBOL: "delete_symbol",
        OperationType.RENAME_SYMBOL: "rename_symbol",
        OperationType.CREATE_FILE: "create_file",
        OperationType.DELETE_FILE: "delete_file",
        OperationType.RENAME_FILE: "rename_file",
        OperationType.MOVE_FILE: "move_file",
        OperationType.UPDATE_IMPORTS: "update_imports",
    }

    def dispatch(self, operation):

        handler = self.HANDLERS.get(operation.operation)

        if handler is None:
            return DispatchResult(
                success=False,
                status=DispatchStatus.UNSUPPORTED,
                handler="",
                message=f"No handler registered for {operation.operation.value}",
            )

        return DispatchResult(
            success=True,
            status=DispatchStatus.DISPATCHED,
            handler=handler,
            message="Handler selected",
        )


edit_operation_router = EditOperationRouter()
