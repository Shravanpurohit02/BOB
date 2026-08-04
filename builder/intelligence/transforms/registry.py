"""
Production-ready transformation registry.
"""

from __future__ import annotations

from typing import Dict, Iterable

from .base import BaseTransform
from .exceptions import UnsupportedTransformError


class TransformRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, BaseTransform] = {}

    def register(self, transform: BaseTransform) -> None:
        if not transform.operation:
            raise ValueError("Transform.operation must not be empty.")
        self._registry[transform.operation] = transform

    def unregister(self, operation: str) -> None:
        self._registry.pop(operation, None)

    def get(self, operation: str) -> BaseTransform:
        try:
            return self._registry[operation]
        except KeyError as exc:
            raise UnsupportedTransformError(
                f"Unknown transform: {operation}"
            ) from exc

    def exists(self, operation: str) -> bool:
        return operation in self._registry

    def operations(self) -> Iterable[str]:
        return tuple(sorted(self._registry))


registry = TransformRegistry()

__all__ = (
    "TransformRegistry",
    "registry",
)
