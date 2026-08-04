"""
Production-ready transformation framework base classes.

This module defines the common interface for every code transformation
implemented by BOB.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TransformContext:
    workspace: str
    transaction: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TransformResult:
    success: bool
    operation: str
    message: str = ""
    patch_id: str = ""
    diff: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTransform(ABC):
    """Abstract base class for all production transformations."""

    operation: str = ""

    def run(self, context: TransformContext, **kwargs) -> TransformResult:
        return self.execute(context=context, **kwargs)

    @abstractmethod
    def execute(
        self,
        context: TransformContext,
        **kwargs,
    ) -> TransformResult:
        """Execute the transformation."""
        raise NotImplementedError
