from __future__ import annotations


class DecisionEngine:

    def decide(self, runtime):

        validation = (
            runtime.context.pipeline.context.validation
            or {}
        )

        if validation.get("failed", 0) == 0:
            return "complete"

        diagnosis = getattr(
            runtime.context,
            "metadata",
            {},
        ).get("diagnosis")

        if diagnosis and diagnosis.get("files"):
            return "repair"

        return "repair"


decision = DecisionEngine()
