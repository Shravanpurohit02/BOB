
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Provider:
    """
    Generic provider configuration and runtime state.
    """

    name: str

    model: str = ""

    enabled: bool = True

    priority: int = 100

    capabilities: set[str] = field(default_factory=set)

    metadata: dict[str, Any] = field(default_factory=dict)

    def supports(
        self,
        capability: str,
    ) -> bool:

        return capability in self.capabilities

    def enable(
        self,
    ) -> None:

        self.enabled = True

    def disable(
        self,
    ) -> None:

        self.enabled = False

    def add_capability(
        self,
        capability: str,
    ) -> None:

        self.capabilities.add(capability)

    def remove_capability(
        self,
        capability: str,
    ) -> None:

        self.capabilities.discard(capability)

    def update(
        self,
        **values: Any,
    ) -> None:

        self.metadata.update(values)

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "name": self.name,
            "model": self.model,
            "enabled": self.enabled,
            "priority": self.priority,
            "capabilities": sorted(self.capabilities),
            "metadata": dict(self.metadata),
        }
