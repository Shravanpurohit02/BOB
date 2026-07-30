from pathlib import Path

from builder.ast.parser import parser

class SymbolIndex:

    def build(self, workspace: str):

        modules = []

        for file in Path(workspace).rglob("*.py"):
            try:
                modules.append(
                    parser.parse(str(file))
                )
            except Exception:
                pass

        return modules

symbols = SymbolIndex()
