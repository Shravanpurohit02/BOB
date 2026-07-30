from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from builder.runtime.runtime import Runtime


@dataclass(slots=True)
class Kernel:
    """
    Core Builder kernel.

    Owns the active runtime together with kernel state,
    shared context and registered services.
    """

    runtime: Runtime

    state: dict[str, Any] = field(default_factory=dict)

    context: dict[str, Any] = field(default_factory=dict)

    services: dict[str, Any] = field(default_factory=dict)

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:

        self.services[name] = service

    def service(
        self,
        name: str,
    ) -> Any | None:

        return self.services.get(name)

    def update(
        self,
        **values: Any,
    ) -> None:

        self.state.update(values)

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.state.get(
            key,
            default,
        )

    def set_context(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.context[key] = value

    def context_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.context.get(
            key,
            default,
        )

    def reset(
        self,
    ) -> None:

        self.state.clear()
        self.context.clear()
        self.services.clear()


