from __future__ import annotations


class HandlerError(Exception):
    """
    Base exception for all handler failures.
    """

    def __init__(
        self,
        message: str,
        *,
        operation: str = "",
        file: str = "",
    ):
        super().__init__(message)
        self.operation = operation
        self.file = file


class ValidationError(HandlerError):
    """
    Raised when handler input validation fails.
    """


class DispatchError(HandlerError):
    """
    Raised when a handler cannot execute an operation.
    """


class PatchError(HandlerError):
    """
    Raised when a patch cannot be created,
    validated, compiled or committed.
    """


class TransactionError(HandlerError):
    """
    Raised when transaction lifecycle operations fail.
    """


class RollbackError(HandlerError):
    """
    Raised when rollback fails.
    """


class UnsupportedOperationError(HandlerError):
    """
    Raised when a handler does not support
    the requested operation.
    """


class SymbolNotFoundError(HandlerError):
    """
    Raised when the requested symbol
    cannot be located.
    """


class FileOperationError(HandlerError):
    """
    Raised for file creation, deletion,
    rename or move failures.
    """
