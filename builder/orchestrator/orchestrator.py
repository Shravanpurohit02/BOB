from pathlib import Path

from builder.analysis import engine as analysis_engine
from builder.ast import engine as ast_engine
from builder.autonomous_runtime.engine import engine as runtime_engine
from builder.codegen import (
    CodeGenerationRequest,
)
from builder.codegen import (
    engine as codegen,
)
from builder.dependency import engine as dependency
from builder.engineering.changeset import engine as ecs
from builder.execution.context import ExecutionContext
from builder.execution.executor import executor
from builder.execution.scheduler import scheduler, worker_pool
from builder.intelligence.change_executor import change_executor
from builder.output.engine import engine as output_engine
from builder.pipeline.engine import engine as pipeline
from builder.project import analyzer, indexer, registry

from .context import BuildContext
from .intent import Intent, classifier


class Orchestrator:
    def execute(self, request):

        workspace = Path(request.workspace).resolve()

        indexer.build(str(workspace))

        ast_data = ast_engine.build(str(workspace))

        deps = dependency.analyze(str(workspace))

        summary = analyzer.summary()

        repository = sorted(f.relative_path for f in registry.all())

        context = BuildContext(
            project=workspace.name,
            files=summary["files"],
            modules=len(ast_data["modules"]),
            dependencies=len(deps["packages"]),
            repository=repository,
        )

        changeset = ecs.create(
            objective=request.objective,
            workspace=str(workspace),
        )

        pipeline_result = pipeline.start(
            objective=request.objective,
            workspace=str(workspace),
        )

        execution_context = ExecutionContext(
            objective=request.objective,
            workspace=str(workspace),
        )

        execution_jobs = [
            type(
                "Job",
                (),
                {
                    "id": "execution",
                    "status": "pending",
                    "priority": 0,
                    "dependencies": [],
                },
            )()
        ]

        execution_context.metadata["execution_order"] = scheduler.schedule(
            execution_jobs
        )

        execution_context.metadata["execution_batches"] = scheduler.schedule_parallel(
            execution_jobs
        )

        worker = worker_pool.acquire()

        if worker is not None:
            execution_context.worker_id = worker["id"]

        execution_result = executor.execute(execution_context)

        if worker is not None:
            worker_pool.release(worker["id"])

        runtime_result = runtime_engine.execute(
            objective=request.objective,
            workspace=str(workspace),
        )

        intent = classifier.classify(request.objective)

        analysis = None

        if intent is Intent.IMPLEMENT:
            change_executor.build(str(workspace))
            _ = change_executor.create_plan(
                request.objective,
            )

        else:
            analysis = analysis_engine.analyze(
                workspace=str(workspace),
                objective=request.objective,
                model=request.model,
            )

        intent = classifier.classify(request.objective)

        if intent in (
            Intent.QUESTION,
            Intent.ANALYZE,
            Intent.AUDIT,
        ):
            analysis = analysis_engine.analyze(
                workspace=str(workspace),
                objective=request.objective,
                model=request.model,
            )

            print("=" * 80)
            print("ANALYSIS")
            print("=" * 80)
            print(analysis.text)
            print("=" * 80)

            return {
                "pipeline": pipeline_result,
                "execution": execution_result,
                "runtime": runtime_result,
                "generation": analysis,
                "changeset": changeset,
            }

        if intent is Intent.IMPLEMENT:

            generation = codegen.generate(
                CodeGenerationRequest(
                    instruction=request.objective,
                    context=str(context),
                    model=request.model,
                    workspace=str(workspace),

                    resolved_files=[
                        op.file
                        for op in _.operations
                    ],

                    resolved_symbols=[
                        s
                        for op in _.operations
                        for s in op.symbols
                    ],

                    operations=list(_.operations),

                    execution_order=[
                        op.file
                        for op in _.operations
                    ],

                    impacts=[
                        i
                        for op in _.operations
                        for i in op.impacts
                    ],

                    risk=getattr(_, "risk", "low"),
                )
            )

        else:
            generation = analysis

        generation = output_engine.apply_generation(
            str(workspace),
            generation,
        )

        for path in generation.generated_files:
            ecs.add_file(
                changeset,
                path,
                "create",
                "AI generated file",
            )

        for path in generation.modified_files:
            ecs.add_file(
                changeset,
                path,
                "modify",
                "AI modified file",
            )

        ecs.report(
            changeset,
            summary="Engineering pipeline completed.",
            recommendations=[
                "Review generated code.",
                "Run regression tests.",
                "Commit approved changes.",
            ],
        )

        ecs.save(changeset)

        return {
            "pipeline": pipeline_result,
            "execution": execution_result,
            "runtime": runtime_result,
            "generation": generation,
            "changeset": changeset,
        }


orchestrator = Orchestrator()
