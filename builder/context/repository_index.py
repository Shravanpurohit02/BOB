from pathlib import Path


class RepositoryIndex:

    IGNORE = {
        ".git",
        ".builder",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        "dist",
        "build",
        ".venv",
        "venv",
    }

    def _ignored(self, path):

        return any(
            part in self.IGNORE
            for part in Path(path).parts
        )

    def build(self, workspace):

        workspace = Path(workspace)

        index = {
            "files": [],
            "python": [],
            "directories": [],
            "extensions": {},
        }

        for item in workspace.rglob("*"):

            if self._ignored(item):
                continue

            if item.is_dir():

                index["directories"].append(
                    str(item)
                )

                continue

            path = str(item)

            index["files"].append(path)

            suffix = item.suffix.lower()

            index["extensions"][suffix] = (
                index["extensions"].get(
                    suffix,
                    0,
                )
                + 1
            )

            if suffix == ".py":
                index["python"].append(path)

        index["files"].sort()
        index["python"].sort()
        index["directories"].sort()

        return index


index = RepositoryIndex()
