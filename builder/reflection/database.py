from __future__ import annotations

from dataclasses import dataclass, field

from builder.reflection.module import Module
from builder.reflection.symbol import Symbol


@dataclass(slots=True)
class ReflectionDatabase:
    """
    Central in-memory reflection database.
    """

    modules: dict[str, Module] = field(default_factory=dict)
    symbols: dict[str, Symbol] = field(default_factory=dict)

    def clear(self) -> None:
        self.modules.clear()
        self.symbols.clear()

    def add_module(self, module: Module) -> None:
        self.modules[module.path] = module

    def add_symbol(self, symbol: Symbol) -> None:
        key = f"{symbol.module}:{symbol.name}"
        self.symbols[key] = symbol

    def module(self, path: str) -> Module | None:
        return self.modules.get(path)

    def symbol(self, qualified_name: str) -> Symbol | None:
        return self.symbols.get(qualified_name)

    def all_modules(self) -> list[Module]:
        return sorted(
            self.modules.values(),
            key=lambda m: m.path,
        )

    def all_symbols(self) -> list[Symbol]:
        return sorted(
            self.symbols.values(),
            key=lambda s: (s.module, s.name),
        )

    def statistics(self) -> dict[str, int]:
        return {
            "modules": len(self.modules),
            "symbols": len(self.symbols),
        }


database = ReflectionDatabase()
