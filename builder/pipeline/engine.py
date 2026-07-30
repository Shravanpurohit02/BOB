from .models import (
    PipelineContext,
    PipelineResult,
)

from builder.engineering.changeset import engine as ecs
from builder.reflection.semantic_engine import engine as semantic
from builder.planning import analyzer
from builder.intelligence.impact import impact
from builder.output import engine as output
from .validator import validator
from .testing import testing_pipeline
from .finalizer import finalizer


class PipelineEngine:

    def start(
        self,
        objective: str,
        workspace: str,
    ):

        ctx = PipelineContext(
            objective=objective,
            workspace=workspace,
        )

        result = PipelineResult(
            success=True,
            context=ctx,
        )

        ctx.changeset = ecs.create(
            objective,
            workspace,
        )
        result.stages.append("changeset")

        ctx.output = output.create(
            objective=objective,
            workspace=workspace,
            metadata={
                "pipeline": "started",
            },
        )
        result.stages.append("output")

        ctx.semantic = semantic.build(workspace)
        result.stages.append("semantic")

        ctx.plan = analyzer.analyze(
            objective,
            workspace,
        )
        result.stages.append("planning")

        target = objective

        if ctx.plan and ctx.plan.impact:
            target = ctx.plan.impact.target

        ctx.impact = impact.analyze(
            workspace,
            target,
        )
        result.stages.append("impact")

        ctx.validation = validator.run(workspace)
        result.stages.append("validation")

        ctx.testing = testing_pipeline.run(workspace)
        result.stages.append("testing")

        ctx.changeset.semantic = ctx.semantic
        ctx.changeset.plan = ctx.plan
        ctx.changeset.impact = ctx.impact
        ctx.changeset.validation = ctx.validation
        ctx.changeset.testing = ctx.testing

        ctx.finalization = finalizer.finish(ctx)
        result.stages.append("finalization")

        ecs.report(
            ctx.changeset,
            summary=(
                f"Engineering analysis completed. "
                f"Risk: {ctx.impact.risk}. "
                f"Modules: {len(ctx.impact.modules)}. "
                f"Validation: {ctx.validation['passed']}/{ctx.validation['files']}. "
                f"Tests: {ctx.testing['passed']}/{ctx.testing['tests']}."
            ),
            recommendations=[
                "Review engineering plan.",
                "Review impact analysis.",
                "Execute planned changes only.",
            ],
            notes=[
                f"Semantic symbols: {len(ctx.semantic.symbols)}",
                f"Repository modules: {len(ctx.semantic.modules)}",
            ],
        )

        ecs.save(ctx.changeset)

        return result


engine = PipelineEngine()
