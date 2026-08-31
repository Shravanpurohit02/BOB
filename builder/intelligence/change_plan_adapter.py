# Production integration patch
from builder.intelligence.operation_types import OperationType

_OPERATION_MAP={
 "replace_exception_handler":OperationType.REPLACE_EXCEPTION_HANDLER,
 "update_subprocess_call":OperationType.UPDATE_SUBPROCESS_CALL,
 "convert_mutable_class_attribute":OperationType.CONVERT_MUTABLE_CLASS_ATTRIBUTE,
}
# Replace operation=operation.operation with:
# operation=_OPERATION_MAP.get(operation.operation, operation.operation)
