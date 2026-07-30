from __future__ import annotations

from pathlib import Path

from builder.project.model import Project


class ProjectIndexer:
    """
    Indexes an entire project workspace.
    """

    IGNORE = {
        ".git",
        ".builder",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "venv",
    }

    def build(
        self,
        workspace: str,
    ) -> Project:

        root = Path(workspace).resolve()

        project = Project(
            root=str(root),
        )

        for item in root.rglob("*"):

            rel = item.relative_to(root).as_posix()

            if any(
                part in self.IGNORE
                for part in item.parts
            ):
                continue

            if item.is_dir():

                project.add_directory(rel)

                if (item / "__init__.py").exists():
                    project.add_package(
                        rel.replace("/", ".")
                    )

                continue

            project.add_file(rel)

            if item.suffix == ".py":
                project.add_module(rel)

        project.modules.sort()
        project.files.sort()
        project.directories.sort()
        project.packages.sort()

        return project

    def modules(
        self,
        workspace: str,
    ) -> list[str]:

        return self.build(
            workspace
        ).modules

    def files(
        self,
        workspace: str,
    ) -> list[str]:

        return self.build(
            workspace
        ).files

    def packages(
        self,
        workspace: str,
    ) -> list[str]:

        return self.build(
            workspace
        ).packages


index = ProjectIndexer()

