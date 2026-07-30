from dataclasses import dataclass, field

from .file_resolver import file_resolver
from .impact_analyzer import impact_analyzer
from .semantic_search import semantic_search
from .symbol_resolution import symbol_resolver


@dataclass(slots=True)
class EngineeringContext:
    query: str

    resolved_files: list[str] = field(default_factory=list)

    resolved_symbols: list = field(default_factory=list)

    related_symbols: list = field(default_factory=list)

    impacts: list = field(default_factory=list)


class EngineeringContextBuilder:

    MAX_RELATED = 10

    def build(self, workspace: str):

        self.workspace = workspace

        file_resolver.build(workspace)
        symbol_resolver.build(workspace)
        semantic_search.build(workspace)
        impact_analyzer.build(workspace)

    def create(self, query: str):

        ctx = EngineeringContext(query=query)

        # --------------------------------------------------
        # File Resolution
        # --------------------------------------------------

        files = file_resolver.resolve(query)

        ctx.resolved_files.extend(files.exact)

        for file in files.partial:
            if file not in ctx.resolved_files:
                ctx.resolved_files.append(file)

        # --------------------------------------------------
        # Symbol Resolution
        # --------------------------------------------------

        resolved = symbol_resolver.resolve(query)

        seen = set()

        for group in (
            resolved.exact,
            resolved.prefix,
            resolved.contains,
        ):

            for symbol in group:

                if symbol.id in seen:
                    continue

                seen.add(symbol.id)

                ctx.resolved_symbols.append(symbol)

        # --------------------------------------------------
        # Semantic Search (fallback)
        # --------------------------------------------------

        if (
            not ctx.resolved_files
            and not ctx.resolved_symbols
        ):

            related = semantic_search.search(
                query,
                limit=self.MAX_RELATED,
            )

            seen = set()

            for symbol in related:

                if symbol.id in seen:
                    continue

                seen.add(symbol.id)

                ctx.related_symbols.append(symbol)

        # --------------------------------------------------
        # Impact Analysis
        # --------------------------------------------------

        processed = set()

        for symbol in (
            ctx.resolved_symbols +
            ctx.related_symbols
        ):

            if symbol.id in processed:
                continue

            processed.add(symbol.id)

            ctx.impacts.append(
                impact_analyzer.analyze(
                    symbol.name
                )
            )

        return ctx


engineering_context_builder = EngineeringContextBuilder()
