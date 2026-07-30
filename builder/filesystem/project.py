from pathlib import Path

from builder.models.project import Project


class ProjectScanner:

    def scan(self, root: Path | str) -> Project:

        root = Path(root).resolve()

        pyprojects = sorted(root.rglob("pyproject.toml"))

        primary = pyprojects[0] if pyprojects else None

        git = root / ".git"

        project = Project(
            root=root,
            name=root.name,
            detected=root.exists(),
            pyproject=primary,
            git=git if git.exists() else None,
        )

        return project


scanner = ProjectScanner()
