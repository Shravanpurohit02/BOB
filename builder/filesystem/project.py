from pathlib import Path

from builder.project.model import Project


class ProjectScanner:
    def scan(self, root: Path | str) -> Project:

        root = Path(root).resolve()

        pyprojects = sorted(root.rglob("pyproject.toml"))

        primary = pyprojects[0] if pyprojects else None

        git = root / ".git"

        project = Project(
            root=str(root),
            name=root.name,
        )

        return project


scanner = ProjectScanner()
