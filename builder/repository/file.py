from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class RepositoryFile:
    """
    Repository file metadata.
    """

    path: str

    size: int = 0

    exists: bool = True

    extension: str = ""

    is_python: bool = False

    @classmethod
    def from_path(
        cls,
        path: str | Path,
    ) -> RepositoryFile:

        path = Path(path)

        return cls(
            path=path.as_posix(),
            size=path.stat().st_size if path.exists() else 0,
            exists=path.exists(),
            extension=path.suffix.lower(),
            is_python=path.suffix.lower() == ".py",
        )

    @property
    def name(
        self,
    ) -> str:

        return Path(self.path).name

    @property
    def stem(
        self,
    ) -> str:

        return Path(self.path).stem

    @property
    def parent(
        self,
    ) -> str:

        return Path(self.path).parent.as_posix()

    def to_dict(
        self,
    ) -> dict:

        return asdict(self)


File = RepositoryFile
