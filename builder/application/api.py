"""Public HTTP API contract for the BOB Android client.

This module contains only transport-level contracts.
BOB's intelligence remains in the existing runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HealthResponse:
    success: bool
    service: str
    status: str
    version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "service": self.service,
            "status": self.status,
            "version": self.version,
        }


@dataclass(frozen=True)
class RunRequest:
    objective: str
    workspace: str | None = None
    session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "objective": self.objective,
        }

        if self.workspace is not None:
            payload["workspace"] = self.workspace

        if self.session_id is not None:
            payload["session_id"] = self.session_id

        return payload
