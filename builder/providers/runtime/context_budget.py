
from __future__ import annotations
from pathlib import Path

from builder.providers.runtime.budget_report import BudgetReport
from builder.providers.runtime.context_selector import context_selector
from builder.providers.runtime.prompt_compressor import prompt_compressor
from builder.providers.runtime.registry import registry
from builder.providers.runtime.token_estimator import token_estimator


class ContextBudgetEngine:

    def build(
        self,
        *,
        provider: str,
        workspace: str,
        objective: str,
    ) -> BudgetReport:

        profile = registry.get(provider)

        selected = context_selector.select(
            workspace,
            objective,
        )

        resolved = context_selector.resolve(
            workspace,
            selected,
        )

        compressed = prompt_compressor.compress_repository(
            resolved,
        )

        selected_files: list[str] = []
        omitted_files: list[str] = []

        prompt = prompt_compressor.build_prompt(
            objective,
            compressed,
        )

        tokens = token_estimator.estimate_text(prompt)
        bytes_ = token_estimator.estimate_bytes(prompt)

        if (
            tokens > profile.usable_input_tokens
            or
            bytes_ > profile.max_request_bytes
        ):

            ranked = sorted(
                compressed.items(),
                key=lambda item: len(item[1]),
                reverse=True,
            )

            while ranked:

                path, _ = ranked.pop()

                compressed.pop(path, None)

                omitted_files.append(
                    Path(path).name,
                )

                prompt = prompt_compressor.build_prompt(
                    objective,
                    compressed,
                )

                tokens = token_estimator.estimate_text(
                    prompt,
                )

                bytes_ = token_estimator.estimate_bytes(
                    prompt,
                )

                if (
                    tokens <= profile.usable_input_tokens
                    and
                    bytes_ <= profile.max_request_bytes
                ):
                    break

        selected_files = sorted(compressed)

        original_size = sum(
            len(text)
            for text in compressed.values()
        ) + sum(
            len(name)
            for name in omitted_files
        )

        final_size = sum(
            len(text)
            for text in compressed.values()
        )

        ratio = (
            1.0
            if original_size == 0
            else round(
                final_size / original_size,
                4,
            )
        )

        return BudgetReport(
            provider=provider,
            estimated_tokens=tokens,
            estimated_bytes=bytes_,
            token_limit=profile.usable_input_tokens,
            byte_limit=profile.max_request_bytes,
            selected_files=selected_files,
            omitted_files=sorted(omitted_files),
            compression_ratio=ratio,
            within_budget=(
                tokens <= profile.usable_input_tokens
                and
                bytes_ <= profile.max_request_bytes
            ),
            metadata={
                "objective": objective,
                "prompt": prompt,
            },
        )


context_budget = ContextBudgetEngine()
