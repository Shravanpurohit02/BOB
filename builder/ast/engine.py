from __future__ import annotations

from builder.ast.call_graph import call_graph
from builder.ast.imports import imports
from builder.ast.parser import parser
from builder.ast.symbol_graph import symbol_graph
from builder.ast.module_indexer import module_indexer


class ASTEngine:
    """
    Unified AST analysis engine.

    Coordinates parsing, symbol indexing, import dependency analysis,
    call graph generation and symbol graph construction.
    """

    def parse(self, path: str):
        return parser.parse(path)

    def parse_workspace(self, workspace: str):
        return module_indexer.build(workspace)

    def imports(self, workspace: str):
        modules = module_indexer.build(workspace)
        return imports.build(modules)

    def reverse_imports(self, workspace: str):
        modules = module_indexer.build(workspace)
        return imports.reverse(modules)

    def symbol_graph(self, workspace: str):
        modules = module_indexer.build(workspace)
        return symbol_graph.build(modules)

    def call_graph(self, workspace: str):
        return call_graph.build(workspace)

    def analyze(self, workspace: str):
        modules = module_indexer.build(workspace)
        return {
            "modules": modules,
            "imports": imports.build(modules),
            "reverse_imports": imports.reverse(modules),
            "symbol_graph": symbol_graph.build(modules),
            "call_graph": call_graph.build(workspace),
        }

    def build(self, workspace: str):
        return self.analyze(workspace)


engine = ASTEngine()
