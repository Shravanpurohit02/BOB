from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Project:
    """
    Represents a detected Builder workspace.

    This model is intentionally lightweight and immutable in structure.
    Existing fields are preserved for backward compatibility.
    """

    root: Path
    name: str
    detected: bool

    pyproject: Path | None = None
    git: Path | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def exists(self) -> bool:
        return self.root.exists()

    @property
    def has_git(self) -> bool:
        return self.git is not None

    @property
    def has_pyproject(self) -> bool:
        return self.pyproject is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "name": self.name,
            "detected": self.detected,
            "pyproject": str(self.pyproject) if self.pyproject else None,
            "git": str(self.git) if self.git else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        return cls(
            root=Path(data["root"]),
            name=data["name"],
            detected=data["detected"],
            pyproject=Path(data["pyproject"]) if data.get("pyproject") else None,
            git=Path(data["git"]) if data.get("git") else None,
            metadata=dict(data.get("metadata", {})),
        )
