import json
from pathlib import Path


class RepositoryMemory:

    def __init__(self):

        self.root = (
            Path(".builder")
            / "memory"
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _file(
        self,
        workspace,
    ):

        name = (
            workspace
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
        )

        return self.root / f"{name}.json"

    def save(
        self,
        workspace,
        data,
    ):

        file = self._file(workspace)

        file.write_text(
            json.dumps(
                data,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return file

    def load(
        self,
        workspace,
    ):

        file = self._file(workspace)

        if not file.exists():
            return {}

        return json.loads(
            file.read_text(
                encoding="utf-8",
            )
        )

    def exists(
        self,
        workspace,
    ):

        return self._file(
            workspace,
        ).exists()


memory = RepositoryMemory()
