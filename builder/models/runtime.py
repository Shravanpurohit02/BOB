from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from builder.models.project import Project


@dataclass(slots=True)
class RuntimeContext:
    """
    Builder session runtime context.

    This model represents the current Builder session and is intentionally
    backward compatible with the existing implementation.
    """

    session_id: str = field(default_factory=lambda: uuid4().hex)
    started_at: datetime = field(default_factory=datetime.utcnow)

    workspace: Path = field(default_factory=Path.cwd)

    environment: str = "development"

    builder_version: str = "0.1.0-alpha.1"

    project: Project | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def workspace_exists(self) -> bool:
        return self.workspace.exists()

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "workspace": str(self.workspace),
            "environment": self.environment,
            "builder_version": self.builder_version,
            "project": (
                self.project.to_dict()
                if self.project
                else None
            ),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuntimeContext":
        return cls(
            session_id=data["session_id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            workspace=Path(data["workspace"]),
            environment=data["environment"],
            builder_version=data["builder_version"],
            project=(
                Project.from_dict(data["project"])
                if data.get("project")
                else None
            ),
            metadata=dict(data.get("metadata", {})),
        )
