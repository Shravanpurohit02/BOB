from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Context:
    """
    Shared kernel context.

    Stores transient information shared between
    Builder subsystems during execution.
    """

    values: dict[str, Any] = field(default_factory=dict)

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.values[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.values.get(
            key,
            default,
        )

    def remove(
        self,
        key: str,
    ) -> None:

        self.values.pop(
            key,
            None,
        )

    def update(
        self,
        values: dict[str, Any],
    ) -> None:

        self.values.update(values)

    def clear(
        self,
    ) -> None:

        self.values.clear()

    def contains(
        self,
        key: str,
    ) -> bool:

        return key in self.values

    def keys(
        self,
    ) -> list[str]:

        return sorted(self.values.keys())

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Context:

        context = cls()

        context.values.update(
            data.get(
                "values",
                {},
            )
        )

        return context
