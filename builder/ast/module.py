from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Module:
    """
    Canonical representation of a Python module.

    This model is shared by the parser, symbol index, dependency graph,
    semantic search, reflection engine, planning engine, context engine,
    patch engine and autonomous engineering pipeline.

    Every field is JSON serializable and backward compatible with the
    original Module dataclass.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    path: str

    name: str = ""
    package: str = ""
    qualified_name: str = ""

    # ------------------------------------------------------------------
    # Filesystem
    # ------------------------------------------------------------------

    absolute_path: str = ""
    relative_path: str = ""
    parent_directory: str = ""

    exists: bool = True
    is_package: bool = False

    language: str = "python"
    encoding: str = "utf-8"
    extension: str = ".py"

    # ------------------------------------------------------------------
    # Documentation
    # ------------------------------------------------------------------

    docstring: str = ""

    # ------------------------------------------------------------------
    # Imports
    # ------------------------------------------------------------------

    imports: list[str] = field(default_factory=list)
    import_from: list[str] = field(default_factory=list)
    imported_symbols: list[str] = field(default_factory=list)
    wildcard_imports: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Symbols
    # ------------------------------------------------------------------

    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    async_functions: list[str] = field(default_factory=list)

    methods: list[str] = field(default_factory=list)
    async_methods: list[str] = field(default_factory=list)

    decorators: list[str] = field(default_factory=list)

    assignments: list[str] = field(default_factory=list)
    global_variables: list[str] = field(default_factory=list)
    constants: list[str] = field(default_factory=list)

    exports: list[str] = field(default_factory=list)
    all_symbols: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    line_count: int = 0
    code_line_count: int = 0
    comment_line_count: int = 0
    blank_line_count: int = 0

    class_count: int = 0
    function_count: int = 0
    async_function_count: int = 0
    method_count: int = 0
    import_count: int = 0
    global_count: int = 0
    symbol_count: int = 0

    complexity: int = 0

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    parser_version: str = ""
    parser_errors: list[str] = field(default_factory=list)
    parser_warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name and self.path:
            self.name = Path(self.path).stem

        if not self.relative_path and self.path:
            self.relative_path = self.path.replace("\\", "/")

        if not self.absolute_path:
            self.absolute_path = self.path

        if not self.parent_directory:
            self.parent_directory = str(Path(self.path).parent).replace("\\", "/")

        if not self.qualified_name:
            self.qualified_name = (
                self.relative_path[:-3].replace("/", ".").replace("\\", ".")
            )

        if not self.package:
            self.package = Path(self.qualified_name).parent.as_posix().replace("/", ".")

        self.refresh()

    def refresh(self) -> None:

        self.class_count = len(self.classes)

        self.function_count = len(self.functions)

        self.async_function_count = len(self.async_functions)

        self.method_count = len(self.methods) + len(self.async_methods)

        self.import_count = len(self.imports) + len(self.import_from)

        self.global_count = len(self.global_variables)

        if not self.exports:
            self.exports = self.classes + self.functions + self.async_functions

        self.all_symbols = sorted(
            set(
                self.classes
                + self.functions
                + self.async_functions
                + self.methods
                + self.async_methods
                + self.global_variables
                + self.constants
                + self.assignments
            )
        )

        self.symbol_count = len(self.all_symbols)

    @property
    def symbols(self) -> list[str]:
        return list(self.all_symbols)

    @property
    def imports_count(self) -> int:
        return self.import_count

    @property
    def has_docstring(self) -> bool:
        return bool(self.docstring.strip())

    @property
    def has_errors(self) -> bool:
        return bool(self.parser_errors)

    @property
    def has_warnings(self) -> bool:
        return bool(self.parser_warnings)

    def add_import(
        self,
        name: str,
    ) -> None:
        if name and name not in self.imports:
            self.imports.append(name)
            self.refresh()

    def add_function(
        self,
        name: str,
    ) -> None:
        if name and name not in self.functions:
            self.functions.append(name)
            self.refresh()

    def add_async_function(
        self,
        name: str,
    ) -> None:
        if name and name not in self.async_functions:
            self.async_functions.append(name)
            self.refresh()

    def add_class(
        self,
        name: str,
    ) -> None:
        if name and name not in self.classes:
            self.classes.append(name)
            self.refresh()

    def add_method(
        self,
        name: str,
    ) -> None:
        if name and name not in self.methods:
            self.methods.append(name)
            self.refresh()

    def add_async_method(
        self,
        name: str,
    ) -> None:
        if name and name not in self.async_methods:
            self.async_methods.append(name)
            self.refresh()

    def add_global(
        self,
        name: str,
    ) -> None:
        if name and name not in self.global_variables:
            self.global_variables.append(name)
            self.refresh()

    def add_constant(
        self,
        name: str,
    ) -> None:
        if name and name not in self.constants:
            self.constants.append(name)
            self.refresh()

    def add_assignment(
        self,
        name: str,
    ) -> None:
        if name and name not in self.assignments:
            self.assignments.append(name)
            self.refresh()

    def add_decorator(
        self,
        name: str,
    ) -> None:
        if name and name not in self.decorators:
            self.decorators.append(name)

    def add_export(
        self,
        name: str,
    ) -> None:
        if name and name not in self.exports:
            self.exports.append(name)
            self.refresh()

    def add_parser_error(
        self,
        message: str,
    ) -> None:
        if message:
            self.parser_errors.append(message)

    def add_parser_warning(
        self,
        message: str,
    ) -> None:
        if message:
            self.parser_warnings.append(message)

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.metadata.get(
            key,
            default,
        )

    def add_tag(
        self,
        tag: str,
    ) -> None:
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def clear_symbols(self) -> None:
        self.classes.clear()
        self.functions.clear()
        self.async_functions.clear()
        self.methods.clear()
        self.async_methods.clear()
        self.global_variables.clear()
        self.constants.clear()
        self.assignments.clear()
        self.exports.clear()
        self.all_symbols.clear()
        self.refresh()

    def merge(
        self,
        other: Module,
    ) -> None:

        for value in other.imports:
            self.add_import(value)

        for value in other.import_from:
            if value not in self.import_from:
                self.import_from.append(value)

        for value in other.imported_symbols:
            if value not in self.imported_symbols:
                self.imported_symbols.append(value)

        for value in other.wildcard_imports:
            if value not in self.wildcard_imports:
                self.wildcard_imports.append(value)

        for value in other.classes:
            self.add_class(value)

        for value in other.functions:
            self.add_function(value)

        for value in other.async_functions:
            self.add_async_function(value)

        for value in other.methods:
            self.add_method(value)

        for value in other.async_methods:
            self.add_async_method(value)

        for value in other.global_variables:
            self.add_global(value)

        for value in other.constants:
            self.add_constant(value)

        for value in other.assignments:
            self.add_assignment(value)

        for value in other.decorators:
            self.add_decorator(value)

        for value in other.exports:
            self.add_export(value)

        self.metadata.update(other.metadata)

        for tag in other.tags:
            self.add_tag(tag)

        self.parser_errors.extend(other.parser_errors)
        self.parser_warnings.extend(other.parser_warnings)

        self.refresh()

    def to_dict(self) -> dict[str, Any]:
        self.refresh()
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Module:
        module = cls(**data)
        module.refresh()
        return module

    def copy(self) -> Module:
        return Module.from_dict(self.to_dict())

    def __len__(self) -> int:
        return self.symbol_count

    def __contains__(
        self,
        symbol: str,
    ) -> bool:
        return symbol in self.all_symbols

    def __iter__(self):
        return iter(self.all_symbols)

    def __bool__(self) -> bool:
        return self.exists

    def __hash__(self) -> int:
        return hash(self.relative_path or self.path)

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, Module):
            return NotImplemented

        return (self.relative_path or self.path) == (other.relative_path or other.path)

    def summary(self) -> dict[str, Any]:
        self.refresh()

        return {
            "path": self.path,
            "qualified_name": self.qualified_name,
            "classes": self.class_count,
            "functions": self.function_count,
            "async_functions": self.async_function_count,
            "methods": self.method_count,
            "imports": self.import_count,
            "globals": self.global_count,
            "symbols": self.symbol_count,
            "lines": self.line_count,
            "complexity": self.complexity,
        }

    def validate(self) -> list[str]:

        issues: list[str] = []

        if not self.path:
            issues.append("missing_path")

        if self.line_count < 0:
            issues.append("invalid_line_count")

        if self.symbol_count < 0:
            issues.append("invalid_symbol_count")

        return issues

    def __repr__(self) -> str:
        return (
            "Module("
            f"path={self.path!r}, "
            f"symbols={self.symbol_count}, "
            f"imports={self.import_count})"
        )
