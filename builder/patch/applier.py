from pathlib import Path

class PatchApplier:

    def apply(self, path: str, updated: str):

        Path(path).write_text(
            updated,
            encoding="utf-8",
        )

applier = PatchApplier()
