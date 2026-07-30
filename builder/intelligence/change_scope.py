from dataclasses import dataclass, field

from .change_planner import change_planner


@dataclass(slots=True)
class ChangeScope:
    query: str
    risk: str

    resolved_files: list[str] = field(default_factory=list)

    resolved_symbols: list = field(default_factory=list)

    related_symbols: list = field(default_factory=list)

    impacts: list = field(default_factory=list)

    modules: list[str] = field(default_factory=list)


class ChangeScopeAnalyzer:

    def build(self, workspace: str):
        change_planner.build(workspace)

    def analyze(self, query: str):

        plan = change_planner.plan(query)

        return ChangeScope(
            query=plan.query,
            risk=plan.risk,
            resolved_files=list(plan.resolved_files),
            resolved_symbols=list(plan.resolved_symbols),
            related_symbols=list(plan.related_symbols),
            impacts=list(plan.impacts),
            modules=list(plan.modules),
        )


change_scope_analyzer = ChangeScopeAnalyzer()
