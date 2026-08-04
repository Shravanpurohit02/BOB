from __future__ import annotations

from .base import BaseHandler


class HandlerRegistry:
    """
    Registry of engineering operation handlers.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, BaseHandler] = {}

    def register(
        self,
        handler: BaseHandler,
    ) -> None:
        self._handlers[handler.operation] = handler

    def unregister(
        self,
        operation: str,
    ) -> None:
        self._handlers.pop(operation, None)

    def get(
        self,
        operation: str,
    ) -> BaseHandler:
        return self._handlers[operation]

    def has(
        self,
        operation: str,
    ) -> bool:
        return operation in self._handlers

    def all(
        self,
    ) -> dict[str, BaseHandler]:
        return dict(self._handlers)

    def clear(
        self,
    ) -> None:
        self._handlers.clear()


registry = HandlerRegistry()

__all__ = (
    "HandlerRegistry",
    "registry",
)
