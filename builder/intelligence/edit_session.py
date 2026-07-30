from dataclasses import dataclass, field
from pathlib import Path

from .edit_context import edit_context_builder


@dataclass(slots=True)
class EditTarget:
    file: str
    exists: bool
    size: int

    symbols: list = field(default_factory=list)

    impacts: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class EditSession:
    query: str
    risk: str

    targets: list[EditTarget] = field(default_factory=list)


class EditSessionBuilder:

    def __init__(self):
        self.workspace: Path | None = None
        self._built = False

    def build(
        self,
        workspace: str,
    ):
        self.workspace = Path(workspace).resolve()

        edit_context_builder.build(
            str(self.workspace)
        )

        self._built = True

    def _ensure(self):

        if self._built:
            return

        if self.workspace is None:
            raise RuntimeError(
                "EditSessionBuilder has not been initialized. "
                "Call build(workspace) before create()."
            )

        self.build(str(self.workspace))

    def create(
        self,
        query: str,
    ):

        self._ensure()

        ctx = edit_context_builder.create(query)

        targets = {}

        for file in ctx.execution_order:

            path = self.workspace / file

            targets[file] = EditTarget(
                file=file,
                exists=path.exists(),
                size=(
                    path.stat().st_size
                    if path.exists()
                    else 0
                ),
            )

        # Attach resolved symbols to their files.
        for symbol in ctx.resolved_symbols:

            file = (
                symbol.module.replace(".", "/")
                + ".py"
            )

            target = targets.get(file)

            if target is not None:
                target.symbols.append(symbol)

        # Attach impacts to files.
        for impact in ctx.impacts:

            for module in impact["affected_modules"]:

                file = (
                    module.replace(".", "/")
                    + ".py"
                )

                target = targets.get(file)

                if target is None:
                    continue

                target.impacts.append(impact)

        # Initialize metadata for later execution.
        for target in targets.values():

            target.metadata.update({
                "action": "replace_symbol",
                "symbol_count": len(target.symbols),
                "impact_count": len(target.impacts),
            })

        return EditSession(
            query=query,
            risk=ctx.risk,
            targets=list(targets.values()),
        )


edit_session_builder = EditSessionBuilder()
