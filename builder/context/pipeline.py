
from __future__ import annotations

from dataclasses import dataclass, field

from builder.ast import engine as ast_engine
from builder.context.architecture import engine as architecture
from builder.context.change_impact import engine as impact_engine
from builder.context.compression import compressor
from builder.context.file_context import context as file_context
from builder.context.file_planner import planner
from builder.context.prompt_builder import builder as prompt_builder
from builder.context.provider_optimizer import optimizer
from builder.context.repository_graph import engine as repository_graph
from builder.context.selector import selector
from builder.dependency import engine as dependency_engine
from builder.project import analyzer, indexer


@dataclass(slots=True)
class ContextPipelineResult:
    project: dict
    modules: list
    dependencies: dict
    repository_graph: dict
    architecture: dict
    impact: dict
    plan: list
    files: list
    prompt: str
    metadata: dict = field(default_factory=dict)


class ContextPipeline:

    def build(self, *, workspace: str, objective: str, budget: int = 12000) -> ContextPipelineResult:
        indexer.build(workspace)

        ast = ast_engine.build(workspace)
        deps = dependency_engine.analyze(workspace)

        imports = ast.get("imports", {})

        # Backward compatibility with newer AST engine.
        if "imports" not in imports:
            imports = {
                "imports": imports,
                "reverse": ast.get("reverse_imports", {}),
            }

        modules = ast.get("modules", [])

        symbols = {
            "exports": {m.path: getattr(m, "exports", []) for m in modules},
            "references": {m.path: getattr(m, "imports", []) for m in modules},
        }

        graph = repository_graph.build(modules, imports, symbols)
        arch = architecture.analyze(graph)

        ranked = selector.select(
            workspace=workspace,
            objective=objective,
            budget=budget,
        )

        changed = [r.path.replace("\\", "/").split(workspace.rstrip("/").split("/")[-1] + "/", 1)[-1]
                   if workspace in r.path else r.path for r in ranked]

        impact = impact_engine.analyze(graph, changed)

        plan = planner.plan(impact, arch, graph)

        files = []
        for item in ranked:
            ctx = file_context.build(item.path)
            if ctx:
                files.append(ctx)

        prompt = prompt_builder.build(
            objective=objective,
            project={
                "summary": analyzer.summary(),
                "dependencies": deps,
            },
            modules=modules,
            files=compressor.compress_files(files, budget),
        )

        optimized = optimizer.optimize(
            provider=None,
            prompt=prompt,
            files=files,
        )

        return ContextPipelineResult(
            project={"summary": analyzer.summary()},
            modules=modules,
            dependencies=deps,
            repository_graph=graph,
            architecture=arch,
            impact=impact,
            plan=plan,
            files=optimized["files"],
            prompt=prompt,
            metadata={
                "budget": optimized["budget"],
                "prompt_tokens": optimized["prompt_tokens"],
                "file_budget": optimized["file_budget"],
            },
        )


pipeline = ContextPipeline()
