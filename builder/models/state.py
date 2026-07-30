from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class BuilderState:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    boot_count: int = 0

    project: str = ""
    workspace: str = ""
    environment: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def initialized(self) -> bool:
        return self.boot_count > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "boot_count": self.boot_count,
            "project": self.project,
            "workspace": self.workspace,
            "environment": self.environment,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuilderState":
        return cls(
            id=data["id"],
            created_at=data["created_at"],
            boot_count=data.get("boot_count", 0),
            project=data.get("project", ""),
            workspace=data.get("workspace", ""),
            environment=data.get("environment", ""),
            metadata=dict(data.get("metadata", {})),
        )
