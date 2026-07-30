from dataclasses import dataclass

from builder.providers.runtime.registry import registry


@dataclass(slots=True)
class ContextBudget:
    context_window: int
    max_output_tokens: int
    available_input_tokens: int


class ContextBudgetEngine:

    DEFAULT_CONTEXT = 8192
    DEFAULT_OUTPUT = 2048
    SAFETY_MARGIN = 1024

    def budget(self, provider: str = "", model: str = "") -> ContextBudget:

        try:
            runtime = registry.get(provider, model)

            context = (
                runtime.context_window
                or self.DEFAULT_CONTEXT
            )

            output = (
                runtime.max_output_tokens
                or self.DEFAULT_OUTPUT
            )

        except Exception:

            context = self.DEFAULT_CONTEXT
            output = self.DEFAULT_OUTPUT

        available = max(
            1024,
            context - output - self.SAFETY_MARGIN,
        )

        return ContextBudget(
            context_window=context,
            max_output_tokens=output,
            available_input_tokens=available,
        )


engine = ContextBudgetEngine()
