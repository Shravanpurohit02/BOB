
from __future__ import annotations
from pathlib import Path

from builder.intelligence.impact import impact


class ContextSelector:

    IGNORE = {
        ".git",
        ".builder",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
    }

    def _repository_files(
        self,
        workspace: str,
    ) -> list[str]:

        root = Path(workspace)

        files: list[str] = []

        for path in root.rglob("*"):

            if any(part in self.IGNORE for part in path.parts):
                continue

            if not path.is_file():
                continue

            files.append(
                path.relative_to(root).as_posix()
            )

        return sorted(files)

    def select(
        self,
        workspace: str,
        objective: str,
    ) -> list[str]:

        report = impact.analyze(
            workspace,
            objective,
        )

        modules = getattr(
            report,
            "modules",
            [],
        )

        if modules:
            return sorted(set(modules))

        return self._repository_files(workspace)

    def resolve(
        self,
        workspace: str,
        files: list[str],
    ) -> list[Path]:

        root = Path(workspace)

        resolved: list[Path] = []

        for file in files:

            path = root / file

            if path.exists():
                resolved.append(path)

        return resolved


context_selector = ContextSelector()
