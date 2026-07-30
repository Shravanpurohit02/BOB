from pathlib import Path

from builder.ast import engine as ast_engine
from builder.codegen import (
    CodeGenerationRequest,
    engine as codegen,
)
from builder.dependency import engine as dependency
from builder.engineering.changeset import engine as ecs
from builder.execution.context import ExecutionContext
from builder.execution.executor import executor
from builder.execution.scheduler import scheduler, worker_pool
from builder.autonomous_runtime.engine import engine as runtime_engine
from builder.pipeline.engine import engine as pipeline
from builder.project import analyzer, indexer, registry
from builder.output.engine import engine as output_engine

from .context import BuildContext


class Orchestrator:

    def execute(self, request):

        workspace = Path(request.workspace).resolve()

        indexer.build(str(workspace))

        ast_data = ast_engine.build(str(workspace))

        deps = dependency.analyze(str(workspace))

        summary = analyzer.summary()

        repository = sorted(
            f.relative_path
            for f in registry.all()
        )

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

        execution_context.metadata["execution_order"] = (
            scheduler.schedule(
                execution_jobs
            )
        )

        execution_context.metadata["execution_batches"] = (
            scheduler.schedule_parallel(
                execution_jobs
            )
        )

        worker = worker_pool.acquire()

        if worker is not None:
            execution_context.worker_id = worker["id"]

        execution_result = executor.execute(
            execution_context
        )

        if worker is not None:
            worker_pool.release(
                worker["id"]
            )

        runtime_result = runtime_engine.execute(
            objective=request.objective,
            workspace=str(workspace),
        )

        generation = codegen.generate(
            CodeGenerationRequest(
                instruction=request.objective,
                context=str(context),
                model=request.model,
                workspace=str(workspace),
            )
        )

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
