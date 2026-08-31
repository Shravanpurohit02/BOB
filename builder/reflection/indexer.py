from __future__ import annotations

from pathlib import Path

from builder.ast.module_indexer import module_indexer as ast_module_indexer
from builder.reflection.database import database
from builder.reflection.module import Module
from builder.reflection.symbol import Symbol


class ReflectionIndexer:
    """
    Builds the reflection database from the AST subsystem.
    """

    def build(self, workspace: str):
        database.clear()

        modules = ast_module_indexer.build(workspace)

        for ast_module in modules:
            module_path = str(ast_module.path)

            module = Module(
                path=module_path,
                name=Path(module_path).stem,
            )

            database.add_module(module)

            for name in getattr(ast_module, "classes", []):
                database.add_symbol(
                    Symbol(
                        module=module.path,
                        name=name,
                        kind="class",
                    )
                )

            for name in getattr(ast_module, "functions", []):
                database.add_symbol(
                    Symbol(
                        module=module.path,
                        name=name,
                        kind="function",
                    )
                )

            for name in getattr(ast_module, "async_functions", []):
                database.add_symbol(
                    Symbol(
                        module=module.path,
                        name=name,
                        kind="async_function",
                    )
                )

        return database

    def modules(self, workspace: str):
        return self.build(workspace).all_modules()

    def symbols(self, workspace: str):
        return self.build(workspace).all_symbols()


indexer = ReflectionIndexer()
