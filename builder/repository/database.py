from __future__ import annotations

from builder.repository.file import RepositoryFile


class RepositoryDatabase:
    """
    In-memory repository file database.
    """

    def __init__(self) -> None:

        self._files: dict[str, RepositoryFile] = {}

    def clear(
        self,
    ) -> None:

        self._files.clear()

    def add(
        self,
        item: RepositoryFile,
    ) -> None:

        self._files[item.path] = item

    def remove(
        self,
        path: str,
    ) -> None:

        self._files.pop(
            path,
            None,
        )

    def get(
        self,
        path: str,
    ) -> RepositoryFile | None:

        return self._files.get(path)

    def exists(
        self,
        path: str,
    ) -> bool:

        return path in self._files

    def files(
        self,
    ) -> list[RepositoryFile]:

        return sorted(
            self._files.values(),
            key=lambda item: item.path,
        )

    def paths(
        self,
    ) -> list[str]:

        return sorted(
            self._files.keys()
        )

    def count(
        self,
    ) -> int:

        return len(self._files)


database = RepositoryDatabase()

