from __future__ import annotations

from pathlib import Path

from builder.project.index import index
from builder.reflection.engine import engine as reflection_engine


class ProjectAnalyzer:
    """
    Produces a high-level analysis of a project workspace.
    """

    def analyze(self, workspace: str) -> dict:
        project = index.build(workspace)
        reflection = reflection_engine.analyze(workspace)
        root = Path(workspace)

        return {
            "root": str(root.resolve()),
            "name": project.name,
            "modules": project.modules,
            "packages": project.packages,
            "files": project.files,
            "directories": project.directories,
            "statistics": {
                "modules": project.module_count,
                "packages": len(project.packages),
                "files": project.file_count,
                "directories": project.directory_count,
                "symbols": len(reflection["symbols"]),
            },
            "reflection": reflection,
        }

    # Backward compatibility
    def summary(self, workspace: str | None = None) -> dict:
        if workspace is None:
            workspace = str(Path.cwd())
        data = self.analyze(workspace)
        return {
            "files": data["statistics"]["files"],
            "modules": data["statistics"]["modules"],
            "packages": data["statistics"]["packages"],
            "directories": data["statistics"]["directories"],
        }

    def statistics(self, workspace: str) -> dict:
        return self.analyze(workspace)["statistics"]

    def modules(self, workspace: str):
        return index.modules(workspace)

    def packages(self, workspace: str):
        return index.packages(workspace)


analyzer = ProjectAnalyzer()
