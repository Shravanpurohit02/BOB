from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Project:
    """
    Canonical project model.

    Represents an indexed workspace and is shared across the
    project, context, engineering and planning subsystems.
    """

    root: str

    name: str = ""

    version: str = ""

    description: str = ""

    python_version: str = ""

    modules: list[str] = field(default_factory=list)

    packages: list[str] = field(default_factory=list)

    files: list[str] = field(default_factory=list)

    directories: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:

        if not self.name:
            self.name = Path(self.root).name

    @property
    def module_count(self) -> int:
        return len(self.modules)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def directory_count(self) -> int:
        return len(self.directories)

    def add_module(
        self,
        path: str,
    ) -> None:

        if path not in self.modules:
            self.modules.append(path)

    def add_file(
        self,
        path: str,
    ) -> None:

        if path not in self.files:
            self.files.append(path)

    def add_directory(
        self,
        path: str,
    ) -> None:

        if path not in self.directories:
            self.directories.append(path)

    def add_package(
        self,
        package: str,
    ) -> None:

        if package not in self.packages:
            self.packages.append(package)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Project:
        return cls(**data)
