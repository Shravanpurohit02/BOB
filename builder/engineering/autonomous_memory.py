import json
from pathlib import Path


class AutonomousEngineeringMemory:

    def __init__(self):

        self.root = (
            Path(".builder")
            / "engineering_memory"
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
        state,
    ):

        file = self._file(workspace)

        file.write_text(
            json.dumps(
                state,
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

    def update(
        self,
        workspace,
        **values,
    ):

        state = self.load(
            workspace,
        )

        state.update(values)

        self.save(
            workspace,
            state,
        )

        return state

    def exists(
        self,
        workspace,
    ):

        return self._file(
            workspace,
        ).exists()


memory = AutonomousEngineeringMemory()
