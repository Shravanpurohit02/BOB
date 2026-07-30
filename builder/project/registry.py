from __future__ import annotations

import hashlib

from builder.project.model import Project


class ProjectRegistry:
    """
    In-memory registry of indexed projects.
    """

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}

    def clear(self) -> None:
        self._projects.clear()

    def add(
        self,
        project: Project,
    ) -> None:
        self._projects[project.root] = project

    def remove(
        self,
        root: str,
    ) -> None:
        self._projects.pop(root, None)

    def get(
        self,
        root: str,
    ) -> Project | None:
        return self._projects.get(root)

    def exists(
        self,
        root: str,
    ) -> bool:
        return root in self._projects

    def all(self) -> list[Project]:
        return sorted(
            self._projects.values(),
            key=lambda p: p.root,
        )

    def roots(self) -> list[str]:
        return sorted(self._projects.keys())

    def count(self) -> int:
        return len(self._projects)

    # Backward compatibility
    def fingerprint(self) -> str:
        digest = hashlib.sha256()

        for root in self.roots():
            digest.update(root.encode("utf-8"))

        return digest.hexdigest()


registry = ProjectRegistry()
