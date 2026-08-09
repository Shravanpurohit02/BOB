from __future__ import annotations

from enum import Enum


class OperationType(str, Enum):
    REPLACE_SYMBOL = "replace_symbol"
    INSERT_SYMBOL = "insert_symbol"
    DELETE_SYMBOL = "delete_symbol"
    RENAME_SYMBOL = "rename_symbol"

    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    RENAME_FILE = "rename_file"
    MOVE_FILE = "move_file"

    UPDATE_IMPORTS = "update_imports"

    REPLACE_EXCEPTION_HANDLER = "replace_exception_handler"
    UPDATE_SUBPROCESS_CALL = "update_subprocess_call"
    CONVERT_MUTABLE_CLASS_ATTRIBUTE = "convert_mutable_class_attribute"


__all__ = (
    "OperationType",
)
