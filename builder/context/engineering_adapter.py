from __future__ import annotations

from pathlib import Path

from builder.context.file_context import context as file_context
from builder.context.repository_audit import audit_repository
from builder.context.compression import compressor
from builder.intelligence.engineering_context import (
    engineering_context_builder,
)


class EngineeringContextAdapter:
    """
    Converts EngineeringContext into prompt-ready repository evidence.

    This adapter is read-only. It does not modify the existing
    context pipeline and is intended to be consumed by audit mode.
    """

    MAX_FILES = 10

    def build(
        self,
        workspace: str,
        objective: str,
        budget: int = 12000,
    ) -> str:

        engineering_context_builder.build(workspace)

        ctx = engineering_context_builder.create(objective)

        if (
            not ctx.resolved_files
            and not ctx.resolved_symbols
            and not ctx.related_symbols
        ):
            return audit_repository.build(workspace)

        parts: list[str] = []

        parts.append("ENGINEERING EVIDENCE")
        parts.append("===================")
        parts.append("")

        if ctx.resolved_files:
            parts.append("Resolved Files")
            parts.append("--------------")

            for path in ctx.resolved_files:
                parts.append(path)

            parts.append("")

        if ctx.resolved_symbols:
            parts.append("Resolved Symbols")
            parts.append("----------------")

            for symbol in ctx.resolved_symbols:
                parts.append(symbol.id)

            parts.append("")

        if ctx.impacts:
            parts.append("Impact Analysis")
            parts.append("---------------")

            for impact in ctx.impacts:
                parts.append(
                    f"{impact['symbol']} | "
                    f"risk={impact['risk']} | "
                    f"modules={', '.join(impact['affected_modules'])}"
                )

            parts.append("")

        shown = 0

        for rel in ctx.resolved_files:

            if shown >= self.MAX_FILES:
                break

            path = Path(workspace) / rel

            info = file_context.build(str(path))

            if not info:
                continue

            parts.extend([
                f"FILE: {rel}",
                "-" * 60,
                info["source"],
                "",
            ])

            shown += 1

        context = "\n".join(parts)

        # Enforce provider context budget before returning.
        return compressor.compress(
            context,
            budget,
        )


adapter = EngineeringContextAdapter()
