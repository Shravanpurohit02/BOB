from dataclasses import dataclass

from builder.providers.chat import Message


@dataclass(slots=True)
class PromptSections:
    system: str
    objective: str
    repository: str
    additional: str = ""


class PromptBuilder:
    DEFAULT_CONTEXT_BUDGET = 12000
    PROFILES = {
        "analyze": "Analyze ONLY the supplied repository context. Do not propose changes unless requested.",
        "audit": "Audit ONLY the supplied repository context. Every finding must include Evidence, Risk, Recommendation and Confidence. Never speculate.",
        "repair": "Produce the minimum safe repair while preserving architecture.",
        "fix": "Fix only the requested issue.",
        "refactor": "Improve maintainability without changing behaviour.",
        "implement": "Implement the requested feature completely.",
        "create": "Create only required files.",
        "review": "Review quality, security, performance and maintainability.",
        "default": "Use the repository as the source of truth.",
    }
    KEYWORDS = (
        ("audit", "audit"),
        ("analyze", "analyze"),
        ("analyse", "analyze"),
        ("repair", "repair"),
        ("fix", "fix"),
        ("refactor", "refactor"),
        ("implement", "implement"),
        ("create", "create"),
        ("review", "review"),
    )

    def resolve_profile(self, objective: str) -> str:
        t = objective.lower()
        for k, p in self.KEYWORDS:
            if k in t:
                return p
        return "default"

    def build(
        self,
        *,
        system_prompt: str,
        objective: str,
        repository_context: str,
        additional_context: str = "",
        context_budget: int | None = None,
    ):
        budget = context_budget or self.DEFAULT_CONTEXT_BUDGET
        repository_context = self._trim(repository_context, budget)
        profile = self.resolve_profile(objective)
        user = f"""ENGINEERING OBJECTIVE
=====================
{objective}

PROFILE
=======
{profile}

PROFILE INSTRUCTIONS
====================
{self.PROFILES[profile]}

REPOSITORY CONTEXT
==================
{repository_context}
"""
        if additional_context.strip():
            user += f"""

ADDITIONAL CONTEXT
==================
{additional_context}
"""
        return [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user.strip()),
        ]

    def estimate_size(self, text: str) -> int:
        return len(text.encode("utf-8"))

    def fits_budget(self, text: str, budget: int) -> bool:
        return self.estimate_size(text) <= budget

    def _trim(self, text: str, budget: int) -> str:
        if self.fits_budget(text, budget):
            return text
        marker = "\n\n...[repository context truncated]..."
        avail = max(0, budget - len(marker.encode()))
        return text.encode()[:avail].decode("utf-8", "ignore") + marker


builder = PromptBuilder()
