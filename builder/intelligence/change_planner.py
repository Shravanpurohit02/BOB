from dataclasses import dataclass, field

from .engineering_context import engineering_context_builder


@dataclass(slots=True)
class ChangePlan:
    query: str
    risk: str

    resolved_files: list[str] = field(default_factory=list)

    resolved_symbols: list = field(default_factory=list)

    related_symbols: list = field(default_factory=list)

    impacts: list = field(default_factory=list)

    modules: list[str] = field(default_factory=list)

    steps: list[str] = field(default_factory=list)


class ChangePlanner:

    def build(self, workspace: str):
        engineering_context_builder.build(workspace)

    def plan(self, query: str):

        ctx = engineering_context_builder.create(query)

        modules = set()
        risks = []

        for impact in ctx.impacts:

            risks.append(impact["risk"])
            modules.update(impact["affected_modules"])

        if "critical" in risks:
            risk = "critical"
        elif "high" in risks:
            risk = "high"
        elif "medium" in risks:
            risk = "medium"
        else:
            risk = "low"

        return ChangePlan(
            query=query,
            risk=risk,

            resolved_files=list(ctx.resolved_files),

            resolved_symbols=list(ctx.resolved_symbols),

            related_symbols=list(ctx.related_symbols),

            impacts=list(ctx.impacts),

            modules=sorted(modules),

            steps=[
                "Resolve files",
                "Resolve symbols",
                "Analyze impact",
                "Build edit plan",
                "Apply edits",
                "Validate",
                "Run regression tests",
            ],
        )


change_planner = ChangePlanner()
