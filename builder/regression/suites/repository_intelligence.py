from builder.ast.module import Module
from builder.context.architecture import engine as architecture
from builder.context.change_impact import engine as impact
from builder.context.cross_reference import engine as cross_reference
from builder.context.file_planner import planner
from builder.context.repository_graph import engine as repository_graph
from builder.context.repository_memory import memory

NAME = "Repository Intelligence"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates repository graph, architecture, impact analysis and planning."


def run() -> bool:

    try:
        a = Module(path="core.py")
        b = Module(path="service.py")
        c = Module(path="api.py")

        imports = {
            "imports": {
                "core.py": [],
                "service.py": ["core.py"],
                "api.py": ["service.py"],
            },
            "reverse": {
                "core.py": ["service.py"],
                "service.py": ["api.py"],
                "api.py": [],
            },
        }

        symbols = {
            "exports": {
                "core.py": ["Core"],
                "service.py": ["Service"],
                "api.py": ["API"],
            },
            "references": {
                "core.py": [],
                "service.py": ["Core"],
                "api.py": ["Service"],
            },
            "definitions": {
                "Core": ["core.py"],
                "Service": ["service.py"],
            },
        }

        graph = repository_graph.build(
            [a, b, c],
            imports,
            symbols,
        )

        refs = cross_reference.build(
            graph,
            symbols,
        )

        arch = architecture.analyze(
            graph,
        )

        change = impact.analyze(
            graph,
            ["core.py"],
        )

        plan = planner.plan(
            change,
            arch,
            graph,
        )

        memory.save(
            "repository-regression",
            {
                "plan": len(plan),
            },
        )

        loaded = memory.load(
            "repository-regression",
        )

        return (
            len(graph) == 3
            and len(refs) == 3
            and change["count"] == 3
            and len(plan) == 3
            and loaded["plan"] == 3
        )

    except Exception:
        return False
