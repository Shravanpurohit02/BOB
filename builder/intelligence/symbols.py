from dataclasses import dataclass, field


@dataclass(slots=True)
class Symbol:

    name:str

    kind:str

    module:str

    line:int


@dataclass(slots=True)
class SymbolIndex:

    modules:dict=field(default_factory=dict)

    symbols:list[Symbol]=field(default_factory=list)
