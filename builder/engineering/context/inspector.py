from pathlib import Path

from .engine import engine


class ContextInspector:

    def inspect(
        self,
        objective: str,
        workspace: str,
    ):

        ctx = engine.create(
            objective=objective,
            workspace=workspace,
        )

        root = Path(workspace)

        for file in root.rglob("*.py"):

            engine.add_file(
                ctx,
                str(file.relative_to(root)),
            )

            engine.add_module(
                ctx,
                ".".join(
                    file.relative_to(root).with_suffix("").parts
                ),
            )

        return ctx


inspector = ContextInspector()
