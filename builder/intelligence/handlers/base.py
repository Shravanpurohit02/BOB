from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter

from .exceptions import HandlerError
from .models import (
    HandlerContext,
    HandlerMetrics,
    HandlerResult,
    HandlerStatus,
)


class BaseHandler(ABC):
    """
    Production base class for all engineering handlers.
    """

    operation: str = ""

    def execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:

        metrics = HandlerMetrics()
        started = perf_counter()

        try:

            self.validate(
                request=request,
                context=context,
            )

            result = self._execute(
                request=request,
                context=context,
            )

            result.operation = self.operation

            if result.success:
                result.status = HandlerStatus.SUCCESS
            elif result.status is HandlerStatus.READY:
                result.status = HandlerStatus.FAILED

        except HandlerError as exc:

            result = HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file=getattr(exc, "file", ""),
                message=str(exc),
                error=type(exc).__name__,
            )

        except Exception as exc:

            result = HandlerResult(
                success=False,
                status=HandlerStatus.FAILED,
                operation=self.operation,
                file="",
                message=str(exc),
                error=type(exc).__name__,
            )

        metrics.finished_at = metrics.started_at
        metrics.duration = round(
            perf_counter() - started,
            6,
        )

        result.metrics = metrics

        return result

    def validate(
        self,
        request,
        context: HandlerContext,
    ) -> None:
        """
        Optional validation hook.
        """

    @abstractmethod
    def _execute(
        self,
        request,
        context: HandlerContext,
    ) -> HandlerResult:
        """
        Execute the engineering operation.
        """
        raise NotImplementedError


__all__ = (
    "BaseHandler",
)
