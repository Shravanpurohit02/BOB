from dataclasses import dataclass, field
from pathlib import Path

from .change_scope import change_scope_analyzer


@dataclass(slots=True)
class EditPlan:
    query: str
    risk: str

    resolved_files: list[str] = field(default_factory=list)
    resolved_symbols: list = field(default_factory=list)
    related_symbols: list = field(default_factory=list)
    impacts: list = field(default_factory=list)

    editable_files: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)


class EditPlanner:

    def build(self, workspace: str):
        self.workspace = Path(workspace)
        change_scope_analyzer.build(workspace)

    def plan(self, query: str):

        scope = change_scope_analyzer.analyze(query)

        editable = []
        missing = []

        for file in scope.resolved_files:

            path = self.workspace / file

            if path.exists():
                editable.append(file)
            else:
                missing.append(file)

        return EditPlan(
            query=query,
            risk=scope.risk,

            resolved_files=list(scope.resolved_files),
            resolved_symbols=list(scope.resolved_symbols),
            related_symbols=list(scope.related_symbols),
            impacts=list(scope.impacts),

            editable_files=editable,
            missing_files=missing,
        )


edit_planner = EditPlanner()
