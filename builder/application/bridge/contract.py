"""Stable application bridge request and response contracts."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class BridgeRequest:
    """Validated request accepted by the application bridge."""

    objective: str
    workspace: str
    provider: str = ""
    model: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string")

        if not isinstance(self.workspace, str) or not self.workspace.strip():
            raise ValueError("workspace must be a non-empty string")

        if not isinstance(self.provider, str):
            raise ValueError("provider must be a string")

        if not isinstance(self.model, str):
            raise ValueError("model must be a string")

        if not isinstance(self.context, dict):
            raise ValueError("context must be an object")


@dataclass(slots=True, frozen=True)
class BridgeResponse:
    """Stable JSON-safe response envelope returned by the bridge."""

    success: bool
    result: dict[str, Any] = field(default_factory=dict)
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "success": self.success,
            "result": self.result,
        }

        if self.error is not None:
            payload["error"] = self.error

        return payload
