from .navigation import navigator
from .reverse_call_graph import reverse_call_graph_builder


class ImpactAnalyzer:

    def __init__(self):
        self._reverse = None

    def build(self, workspace: str):
        navigator.build(workspace)
        self._reverse = reverse_call_graph_builder.build(workspace)

    def analyze(self, symbol: str):

        definitions = navigator.find_definition(symbol)
        references = navigator.find_references(symbol)
        usages = navigator.find_usages(symbol)
        callers = sorted(self._reverse.get(symbol, []))

        modules = sorted({
            d.module for d in definitions
        } | {
            r.module for r in references
        })

        if len(callers) > 50 or len(usages) > 500:
            risk = "critical"
        elif len(callers) > 20 or len(usages) > 100:
            risk = "high"
        elif len(callers) > 5 or len(usages) > 20:
            risk = "medium"
        else:
            risk = "low"

        return {
            "symbol": symbol,
            "definitions": definitions,
            "references": references,
            "usages": usages,
            "callers": callers,
            "affected_modules": modules,
            "risk": risk,
        }


impact_analyzer = ImpactAnalyzer()
