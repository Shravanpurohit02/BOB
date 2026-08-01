from __future__ import annotations
from typing import ClassVar

from pathlib import Path

from builder.repository.database import database
from builder.repository.file import RepositoryFile


class RepositoryIndex:
    """
    Builds and maintains the repository file index.
    """

    IGNORE = {
        "__pycache__",
        ".git",
        ".builder",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
    }

    def build(
        self,
        workspace: str,
    ):

        database.clear()

        root = Path(workspace).resolve()

        for item in root.rglob("*"):
            if not item.is_file():
                continue

            if any(part in self.IGNORE for part in item.parts):
                continue

            relative = item.relative_to(root)

            database.add(RepositoryFile.from_path(relative))

        return database

    def files(
        self,
        workspace: str,
    ) -> list[RepositoryFile]:

        return self.build(workspace).files()

    def python_files(
        self,
        workspace: str,
    ) -> list[RepositoryFile]:

        return [file for file in self.files(workspace) if file.is_python]

    def get(
        self,
        workspace: str,
        path: str,
    ) -> RepositoryFile | None:

        self.build(workspace)

        return database.get(path)


index = RepositoryIndex()