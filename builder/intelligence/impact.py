from builder.reflection.navigator import navigator

from builder.intelligence.models import (
    ImpactModule,
    ImpactReport,
    ImpactSymbol,
)


class ImpactAnalyzer:

    def analyze(
        self,
        workspace: str,
        target: str,
    ):

        report = ImpactReport(target=target)

        symbol = navigator.symbol(
            workspace,
            target,
        )

        if symbol is not None:
            report.symbols.append(
                ImpactSymbol(
                    name=symbol.name,
                    module=symbol.module,
                    kind=symbol.kind,
                )
            )

        report.references = [
            {"module": module}
            for module in navigator.symbol_modules(
                workspace,
                target,
            )
        ]

        affected = {
            ref["module"]
            for ref in report.references
        }

        report.modules = [
            ImpactModule(name=module)
            for module in sorted(affected)
        ]

        report.validation_scope = sorted(affected)

        if len(affected) > 25:
            report.risk = "high"
        elif len(affected) > 5:
            report.risk = "medium"
        else:
            report.risk = "low"

        return report


impact = ImpactAnalyzer()
