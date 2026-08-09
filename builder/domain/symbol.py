from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class Symbol:
    """
    Canonical symbol model used across Builder.
    """

    id: str = field(default_factory=lambda: uuid4().hex)

    module: str = ""

    name: str = ""

    kind: str = ""

    line: int = 0

    cls: str | None = None

    qualified_name: str = ""

    file: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.qualified_name:
            if self.cls:
                self.qualified_name = (
                    f"{self.module}.{self.cls}.{self.name}"
                )
            else:
                self.qualified_name = (
                    f"{self.module}.{self.name}"
                )

    @property
    def display_name(self) -> str:
        return self.qualified_name
