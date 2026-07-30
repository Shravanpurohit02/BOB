from pathlib import Path

from builder.patch import engine as patch_engine


class Applier:

    def apply(self, path, code):

        target = Path(path)

        if not target.exists():
            return {
                "success": False,
                "reason": "Target file not found.",
            }

        try:

            patch = patch_engine.apply(
                path=str(target),
                updated=code,
                action="modify",
            )

            return {
                "success": True,
                "path": str(target),
                "patch_id": patch.id,
                "validated": patch.validated,
                "compiled": patch.compiled,
                "committed": patch.committed,
            }

        except Exception as exc:

            return {
                "success": False,
                "path": str(target),
                "reason": str(exc),
                "rolled_back": True,
            }


applier = Applier()
