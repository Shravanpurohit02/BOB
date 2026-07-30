from dataclasses import dataclass, field

from .edit_planner import edit_planner


@dataclass(slots=True)
class EditContext:
    query: str
    risk: str

    resolved_files: list[str] = field(default_factory=list)
    resolved_symbols: list = field(default_factory=list)
    related_symbols: list = field(default_factory=list)
    impacts: list = field(default_factory=list)

    editable_files: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)


class EditContextBuilder:

    def __init__(self):
        self.workspace = None
        self._built = False

    def build(self, workspace: str):
        self.workspace = workspace
        edit_planner.build(workspace)
        self._built = True

    def _ensure(self):
        if self._built:
            return

        if self.workspace is None:
            raise RuntimeError(
                "EditContextBuilder has not been initialized. "
                "Call build(workspace) before create()."
            )

        self.build(self.workspace)

    def create(self, query: str):

        self._ensure()

        plan = edit_planner.plan(query)

        execution_order = []
        execution_order.extend(plan.editable_files)
        execution_order.extend(plan.missing_files)

        return EditContext(
            query=query,
            risk=plan.risk,

            resolved_files=list(plan.resolved_files),
            resolved_symbols=list(plan.resolved_symbols),
            related_symbols=list(plan.related_symbols),
            impacts=list(plan.impacts),

            editable_files=list(plan.editable_files),
            missing_files=list(plan.missing_files),

            execution_order=execution_order,
        )


edit_context_builder = EditContextBuilder()
