from __future__ import annotations

import ast
from pathlib import Path

from builder.ast.module import Module


class ASTParser:
    """
    Production Python AST parser.

    Extracts structural information from Python source files and
    populates Module objects for downstream indexing, dependency
    analysis, semantic search, and engineering components.
    """

    def parse(
        self,
        path: str,
    ) -> Module:

        source = Path(path).read_text(
            encoding="utf-8",
        )

        return self.parse_source(
            source=source,
            path=path,
        )

    def parse_source(
        self,
        *,
        source: str,
        path: str,
    ) -> Module:

        module = Module(path=path)

        module.absolute_path = str(
            Path(path).resolve()
        )

        module.relative_path = path.replace(
            "\\",
            "/",
        )

        module.parent_directory = str(
            Path(path).parent
        )

        module.name = Path(path).stem

        module.package = (
            Path(path)
            .parent
            .as_posix()
            .replace("/", ".")
        )

        module.qualified_name = (
            module.relative_path[:-3]
            .replace("/", ".")
            .replace("\\", ".")
        )

        module.line_count = len(
            source.splitlines()
        )

        module.blank_line_count = sum(
            1
            for line in source.splitlines()
            if not line.strip()
        )

        module.code_line_count = sum(
            1
            for line in source.splitlines()
            if line.strip()
            and not line.lstrip().startswith("#")
        )

        module.comment_line_count = sum(
            1
            for line in source.splitlines()
            if line.lstrip().startswith("#")
        )

        try:
            tree = ast.parse(
                source,
                filename=path,
            )
        except SyntaxError as exc:
            module.add_parser_error(
                str(exc)
            )
            return module

        module.docstring = (
            ast.get_docstring(tree)
            or ""
        )

        self._visit(
            tree,
            module,
        )

        module.refresh()

        return module

    def _visit(
        self,
        tree: ast.AST,
        module: Module,
    ) -> None:

        for node in ast.walk(tree):

            if isinstance(node, ast.ClassDef):

                module.add_class(node.name)

                for dec in node.decorator_list:
                    name = self._decorator_name(dec)
                    if name:
                        module.add_decorator(name)

                for item in node.body:

                    if isinstance(
                        item,
                        ast.FunctionDef,
                    ):
                        module.add_method(item.name)

                    elif isinstance(
                        item,
                        ast.AsyncFunctionDef,
                    ):
                        module.add_async_method(
                            item.name
                        )

            elif isinstance(
                node,
                ast.FunctionDef,
            ):

                if not isinstance(
                    getattr(node, "parent", None),
                    ast.ClassDef,
                ):

                    module.add_function(node.name)

                for dec in node.decorator_list:
                    name = self._decorator_name(dec)
                    if name:
                        module.add_decorator(name)

            elif isinstance(
                node,
                ast.AsyncFunctionDef,
            ):

                if not isinstance(
                    getattr(node, "parent", None),
                    ast.ClassDef,
                ):

                    module.add_async_function(
                        node.name
                    )

                for dec in node.decorator_list:
                    name = self._decorator_name(dec)
                    if name:
                        module.add_decorator(name)

            elif isinstance(
                node,
                ast.Import,
            ):

                for alias in node.names:
                    module.add_import(alias.name)

            elif isinstance(
                node,
                ast.ImportFrom,
            ):

                if node.module:
                    module.import_from.append(
                        node.module
                    )

                for alias in node.names:

                    module.imported_symbols.append(
                        alias.name
                    )

                    if alias.name == "*":
                        module.wildcard_imports.append(
                            node.module or ""
                        )

            elif isinstance(
                node,
                ast.Assign,
            ):

                for target in node.targets:

                    if isinstance(
                        target,
                        ast.Name,
                    ):

                        module.add_assignment(
                            target.id
                        )

                        if target.id.isupper():
                            module.add_constant(
                                target.id
                            )
                        else:
                            module.add_global(
                                target.id
                            )


        self._attach_parents(tree)

    def _attach_parents(
        self,
        tree: ast.AST,
    ) -> None:

        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child.parent = parent

    def _decorator_name(
        self,
        decorator: ast.AST,
    ) -> str:

        if isinstance(
            decorator,
            ast.Name,
        ):
            return decorator.id

        if isinstance(
            decorator,
            ast.Attribute,
        ):
            return decorator.attr

        if isinstance(
            decorator,
            ast.Call,
        ):
            return self._decorator_name(
                decorator.func
            )

        return ""

    def parse_many(
        self,
        paths: list[str],
    ) -> list[Module]:

        modules: list[Module] = []

        for path in paths:

            try:
                modules.append(
                    self.parse(path)
                )

            except Exception as exc:

                module = Module(path=path)

                module.add_parser_error(
                    str(exc)
                )

                modules.append(module)

        return modules

    def parse_workspace(
        self,
        workspace: str,
    ) -> list[Module]:

        root = Path(workspace)

        return self.parse_many(
            sorted(
                str(file)
                for file in root.rglob("*.py")
            )
        )


parser = ASTParser()

