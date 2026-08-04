"""
Production-ready exceptions for the BOB transformation framework.
"""

from __future__ import annotations


class TransformError(Exception):
    """Base exception for transformation failures."""


class ValidationError(TransformError):
    """Raised when a transformation request is invalid."""


class SymbolNotFoundError(TransformError):
    """Raised when a requested symbol cannot be resolved."""


class TransactionError(TransformError):
    """Raised when a transactional patch fails."""


class RollbackError(TransformError):
    """Raised when rollback cannot be completed."""


class UnsupportedTransformError(TransformError):
    """Raised when a transformation is not implemented or registered."""
