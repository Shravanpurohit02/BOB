from pathlib import Path

class Workspace:

    def __init__(self, root: Path):
        self.root = root.resolve()

    @property
    def exists(self) -> bool:
        return self.root.exists()

    def mkdir(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
