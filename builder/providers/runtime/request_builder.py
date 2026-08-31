from __future__ import annotations

from builder.providers.runtime.context_budget import context_budget


class RequestBuilder:

    def build(
        self,
        *,
        provider: str,
        workspace: str,
        objective: str,
        system_prompt: str = "",
    ) -> dict:
        report = context_budget.build(
            provider=provider,
            workspace=workspace,
            objective=objective,
        )

        return {
            "provider": provider,
            "system": system_prompt.strip(),
            "user": report.metadata["prompt"],
            "budget": report,
        }


request_builder = RequestBuilder()
