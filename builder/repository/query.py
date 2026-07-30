from __future__ import annotations

from builder.repository.database import database
from builder.repository.index import index


class RepositoryQuery:
    """
    Query interface for the repository index.
    """

    def build(
        self,
        workspace: str,
    ):
        return index.build(workspace)

    def all(
        self,
        workspace: str,
    ):
        return self.build(
            workspace
        ).files()

    def get(
        self,
        workspace: str,
        path: str,
    ):
        self.build(workspace)
        return database.get(path)

    def exists(
        self,
        workspace: str,
        path: str,
    ) -> bool:
        self.build(workspace)
        return database.exists(path)

    def python_files(
        self,
        workspace: str,
    ):
        return [
            file
            for file in self.all(workspace)
            if file.is_python
        ]

    def extension(
        self,
        workspace: str,
        suffix: str,
    ):
        suffix = suffix.lower()

        if not suffix.startswith("."):
            suffix = "." + suffix

        return [
            file
            for file in self.all(workspace)
            if file.extension == suffix
        ]

    def search(
        self,
        workspace: str,
        text: str,
    ):
        text = text.lower()

        return [
            file
            for file in self.all(workspace)
            if text in file.path.lower()
        ]


query = RepositoryQuery()

