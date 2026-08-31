from __future__ import annotations

from dataclasses import dataclass, field

from builder.intelligence.ast_rename import (
    RenameResult,
    ast_rename_engine,
)
from builder.intelligence.reference_resolver import (
    reference_resolver,
)
from builder.intelligence.symbol_resolution import (
    symbol_resolver,
)


@dataclass(slots=True)
class SemanticRenameResult:
    success: bool

    symbol: str

    new_name: str

    results: list[RenameResult] = field(default_factory=list)

    message: str = ""


class SemanticRenameEngine:
    def __init__(self):
        self.workspace = None

    def build(
        self,
        workspace: str,
    ):
        self.workspace = workspace

        symbol_resolver.build(workspace)
        reference_resolver.build(workspace)

    def rename(
        self,
        symbol_name: str,
        new_name: str,
    ) -> SemanticRenameResult:

        resolved = symbol_resolver.resolve(symbol_name)

        if not resolved.exact:
            return SemanticRenameResult(
                success=False,
                symbol=symbol_name,
                new_name=new_name,
                message="Symbol not found.",
            )

        target = resolved.exact[0]

        refs = reference_resolver.resolve_qualified(
            target.module,
            target.name,
        )

        results = []

        processed = set()

        for ref in refs.exact:

            if ref.file in processed:
                continue

            processed.add(ref.file)

            result = ast_rename_engine.rename(
                file=ref.file,
                old_name=target.name,
                new_name=new_name,
            )

            results.append(result)

        success = all(r.success for r in results)

        return SemanticRenameResult(
            success=success,
            symbol=symbol_name,
            new_name=new_name,
            results=results,
            message=(
                "Semantic rename completed."
                if success
                else "Semantic rename incomplete."
            ),
        )


semantic_rename_engine = SemanticRenameEngine()

__all__ = (
    "SemanticRenameEngine",
    "SemanticRenameResult",
    "semantic_rename_engine",
)
