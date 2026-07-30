from builder.context.cache import cache
from builder.context.pipeline import pipeline
from builder.context.engineering_adapter import adapter as engineering_adapter
from builder.project import indexer, registry


class ContextEngine:

    def create(
        self,
        workspace: str,
        objective: str,
        budget: int = 12000,
    ) -> str:

        if "audit" in objective.lower():
            return engineering_adapter.build(
                workspace,
                objective,
                budget,
            )

        indexer.build(workspace)

        fingerprint = registry.fingerprint()

        cached = cache.get(
            workspace,
            objective,
            fingerprint,
        )

        if cached is not None:
            return cached["value"]

        result = pipeline.build(
            workspace=workspace,
            objective=objective,
            budget=budget,
        )

        prompt = result.prompt

        cache.put(
            workspace,
            objective,
            prompt,
            fingerprint,
        )

        return prompt


engine = ContextEngine()
