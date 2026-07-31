from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from typing import Any


@dataclass(slots=True)
class KernelState:
    """
    Persistent state for the Builder kernel.
    """

    status: str = "idle"

    started_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    updated_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    values: dict[str, Any] = field(
        default_factory=dict
    )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.values[key] = value
        self.touch()

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

        self.touch()

    def clear(
        self,
    ) -> None:

        self.values.clear()
        self.touch()

    def touch(
        self,
    ) -> None:

        self.updated_at = (
            datetime.now(UTC).isoformat()
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "KernelState":

        state = cls()

        state.status = data.get(
            "status",
            state.status,
        )

        state.started_at = data.get(
            "started_at",
            state.started_at,
        )

        state.updated_at = data.get(
            "updated_at",
            state.updated_at,
        )

        state.values.update(
            data.get(
                "values",
                {},
            )
        )

        return state


