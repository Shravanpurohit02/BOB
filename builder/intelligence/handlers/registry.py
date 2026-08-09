from __future__ import annotations

from collections.abc import Iterator

from .base import BaseHandler
from .exceptions import (
    UnsupportedOperationError,
)


class HandlerRegistry:
    """
    Production registry for engineering handlers.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, BaseHandler] = {}

    def register(
        self,
        handler: BaseHandler,
    ) -> BaseHandler:

        operation = handler.operation.strip()

        if not operation:
            raise ValueError(
                "Handler.operation must not be empty."
            )

        if operation in self._handlers:
            raise ValueError(
                f"Handler already registered: {operation}"
            )

        self._handlers[operation] = handler

        return handler

    def unregister(
        self,
        operation: str,
    ) -> None:
        self._handlers.pop(operation, None)

    def get(
        self,
        operation: str,
    ) -> BaseHandler:

        try:
            return self._handlers[operation]
        except KeyError as exc:
            raise UnsupportedOperationError(
                f"Unknown handler: {operation}",
                operation=operation,
            ) from exc

    def has(
        self,
        operation: str,
    ) -> bool:
        return operation in self._handlers

    def clear(self) -> None:
        self._handlers.clear()

    def operations(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def values(self) -> tuple[BaseHandler, ...]:
        return tuple(
            self._handlers[k]
            for k in sorted(self._handlers)
        )

    def items(
        self,
    ) -> tuple[tuple[str, BaseHandler], ...]:
        return tuple(
            (k, self._handlers[k])
            for k in sorted(self._handlers)
        )

    def __contains__(
        self,
        operation: str,
    ) -> bool:
        return operation in self._handlers

    def __len__(self) -> int:
        return len(self._handlers)

    def __iter__(self) -> Iterator[BaseHandler]:
        return iter(self.values())


registry = HandlerRegistry()

__all__ = (
    "HandlerRegistry",
    "registry",
)
