from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Runtime:
    """
    Runtime information for a Builder session.
    """

    workspace: str

    started_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    version: str = "1.0"

    python_version: str = ""

    platform: str = ""

    state: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def workspace_path(self) -> Path:
        return Path(self.workspace)

    @property
    def running(self) -> bool:
        return self.workspace_path.exists()

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

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workspace": self.workspace,
            "started_at": self.started_at,
            "version": self.version,
            "python_version": self.python_version,
            "platform": self.platform,
            "state": dict(self.state),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Runtime":

        runtime = cls(
            workspace=data["workspace"],
        )

        runtime.started_at = data.get(
            "started_at",
            runtime.started_at,
        )

        runtime.version = data.get(
            "version",
            runtime.version,
        )

        runtime.python_version = data.get(
            "python_version",
            "",
        )

        runtime.platform = data.get(
            "platform",
            "",
        )

        runtime.state.update(
            data.get("state", {})
        )

        runtime.metadata.update(
            data.get("metadata", {})
        )

        return runtime


