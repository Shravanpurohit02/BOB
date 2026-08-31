from __future__ import annotations

from pathlib import Path


class PatchApplier:
    def apply(
        self,
        path: str,
        updated: str,
        *,
        action: str = "modify",
    ) -> None:

        target = Path(path)

        if action == "delete":
            target.unlink(
                missing_ok=True,
            )
            return

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            updated,
            encoding="utf-8",
        )


applier = PatchApplier()

__all__ = (
    "PatchApplier",
    "applier",
)
