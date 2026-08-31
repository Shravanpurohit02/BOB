"""
Production-ready transformation execution context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4
from typing import Any

from .models import TransformBatch


@dataclass(slots=True)
class TransformExecutionContext:
    id: str = field(default_factory=lambda: uuid4().hex)

    workspace: str = "."
    objective: str = ""

    batch: TransformBatch | None = None

    transaction: Any | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    options: dict[str, Any] = field(default_factory=dict)

    def set_option(self, key: str, value: Any) -> None:
        self.options[key] = value

    def get_option(self, key: str, default: Any = None) -> Any:
        return self.options.get(key, default)

    def update_metadata(self, **values: Any) -> None:
        self.metadata.update(values)


__all__ = (
    "TransformExecutionContext",
)
