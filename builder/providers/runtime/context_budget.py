from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from builder.providers.runtime.budget_report import BudgetReport
from builder.providers.runtime.context_selector import context_selector
from builder.providers.runtime.prompt_compressor import prompt_compressor
from builder.providers.runtime.registry import registry as default_registry


@dataclass(slots=True)
class ContextBudget:
    context_window: int
    max_output_tokens: int
    available_input_tokens: int


class ContextBudgetEngine:
    """Resolve provider limits and build bounded repository context."""

    DEFAULT_CONTEXT = 8192
    DEFAULT_OUTPUT = 2048
    SAFETY_MARGIN = 1024

    def __init__(self, registry=None):
        if registry is None:
            # Resolve the package-level object at construction time so tests
            # and runtime integrations can replace context_budget.registry.
            from builder.providers.runtime import context_budget as package_context_budget

            registry = getattr(
                package_context_budget,
                "registry",
                default_registry,
            )

        self.registry = registry

    def _resolve_runtime(
        self,
        provider: str = "",
        model: str = "",
    ):
        return self.registry.get(
            provider=provider,
            model=model,
        )

    def budget(
        self,
        provider: str = "",
        model: str = "",
    ) -> ContextBudget:
        runtime = self._resolve_runtime(
            provider=provider,
            model=model,
        )

        if runtime is None:
            context = self.DEFAULT_CONTEXT
            output = self.DEFAULT_OUTPUT
        else:
            context = (
                runtime.context_window
                or self.DEFAULT_CONTEXT
            )
            output = (
                runtime.max_output_tokens
                or self.DEFAULT_OUTPUT
            )

        available = max(
            1024,
            context - output - self.SAFETY_MARGIN,
        )

        return ContextBudget(
            context_window=context,
            max_output_tokens=output,
            available_input_tokens=available,
        )

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        if not text:
            return 0
        return max(1, (len(text.encode("utf-8")) + 3) // 4)

    def build(
        self,
        *,
        provider: str = "",
        model: str = "",
        workspace: str = "",
        objective: str = "",
    ) -> BudgetReport:
        limits = self.budget(
            provider=provider,
            model=model,
        )

        selected = context_selector.select(
            workspace,
            objective,
        ) if workspace else []

        paths = context_selector.resolve(
            workspace,
            selected,
        ) if workspace else []

        compressed = prompt_compressor.compress_repository(paths)

        prompt = prompt_compressor.build_prompt(
            objective,
            compressed,
        )

        token_limit = limits.available_input_tokens
        byte_limit = max(0, token_limit * 4)

        selected_files: list[str] = []
        omitted_files: list[str] = []
        accepted: list[str] = []
        estimated_tokens = 0
        estimated_bytes = 0

        for file in sorted(compressed):
            content = compressed[file]
            section = f"### FILE: {file}\n{content}\n"
            section_tokens = self._estimate_tokens(section)
            section_bytes = len(section.encode("utf-8"))

            if (
                estimated_tokens + section_tokens <= token_limit
                and estimated_bytes + section_bytes <= byte_limit
            ):
                accepted.append(file)
                selected_files.append(
                    str(Path(file))
                )
                estimated_tokens += section_tokens
                estimated_bytes += section_bytes
            else:
                omitted_files.append(str(Path(file)))

        accepted_files = {
            file: compressed[file]
            for file in accepted
        }

        prompt = prompt_compressor.build_prompt(
            objective,
            accepted_files,
        )

        estimated_tokens = self._estimate_tokens(prompt)
        estimated_bytes = len(prompt.encode("utf-8"))

        original_bytes = sum(
            len(text.encode("utf-8"))
            for text in compressed.values()
        )

        compression_ratio = (
            estimated_bytes / original_bytes
            if original_bytes
            else 1.0
        )

        return BudgetReport(
            provider=provider,
            estimated_tokens=estimated_tokens,
            estimated_bytes=estimated_bytes,
            token_limit=token_limit,
            byte_limit=byte_limit,
            selected_files=selected_files,
            omitted_files=omitted_files,
            compression_ratio=compression_ratio,
            within_budget=(
                estimated_tokens <= token_limit
                and estimated_bytes <= byte_limit
            ),
            metadata={
                "prompt": prompt,
                "context_window": limits.context_window,
                "max_output_tokens": limits.max_output_tokens,
                "available_input_tokens": limits.available_input_tokens,
            },
        )


engine = ContextBudgetEngine()
context_budget = ContextBudgetEngine()
