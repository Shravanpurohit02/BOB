from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LintRule:
    """
    Maps a lint rule to an engineering operation.
    """

    rule: str
    operation: str
    description: str


class LintRuleRegistry:
    """
    Registry of supported lint rules.
    """

    def __init__(self):
        self._rules: dict[str, LintRule] = {}

    def register(
        self,
        rule: str,
        operation: str,
        description: str,
    ) -> None:
        self._rules[rule] = LintRule(
            rule=rule,
            operation=operation,
            description=description,
        )

    def get(
        self,
        rule: str,
    ) -> LintRule | None:
        return self._rules.get(rule)

    def supported(self) -> list[str]:
        return sorted(self._rules)


lint_rule_registry = LintRuleRegistry()

# ----------------------------------------------------------------------
# Initial production rules
# ----------------------------------------------------------------------

lint_rule_registry.register(
    "BLE001",
    "replace_exception_handler",
    "Replace broad exception handlers with explicit exception handling.",
)

lint_rule_registry.register(
    "PLW1510",
    "update_subprocess_call",
    "Add an explicit check= argument to subprocess.run().",
)

lint_rule_registry.register(
    "RUF012",
    "convert_mutable_class_attribute",
    "Replace mutable class attributes with safe alternatives.",
)

lint_rule_registry.register(
    "SIM102",
    "simplify_nested_if",
    "Combine nested if statements.",
)

lint_rule_registry.register(
    "F821",
    "resolve_undefined_name",
    "Resolve undefined identifiers.",
)

__all__ = (
    "LintRule",
    "LintRuleRegistry",
    "lint_rule_registry",
)
