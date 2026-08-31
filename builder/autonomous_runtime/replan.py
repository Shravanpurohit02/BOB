from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .diagnosis import FailureDiagnosis


@dataclass(slots=True, frozen=True)
class ReplanResult:
    """
    Deterministic failure-aware planning decision.

    A replan does not modify files. It changes the planning input for the
    next autonomous attempt so that the planner receives the previous
    validation failure and reliable learned knowledge as explicit
    engineering constraints.
    """

    objective: str
    strategy: str
    attempt: int
    files: tuple[str, ...] = ()
    issues: tuple[dict[str, Any], ...] = ()
    validators: tuple[str, ...] = ()
    learned_context: tuple[dict[str, Any], ...] = ()
    reason: str = ""

    def as_metadata(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "strategy": self.strategy,
            "attempt": self.attempt,
            "files": list(self.files),
            "issues": [
                dict(issue)
                for issue in self.issues
            ],
            "validators": list(self.validators),
            "learned_context": [
                dict(item)
                for item in self.learned_context
            ],
            "reason": self.reason,
        }


class ReplanEngine:

    def replan(
        self,
        *,
        objective: str,
        diagnosis: FailureDiagnosis,
        attempt: int,
        learned_context: list[dict[str, Any]] | None = None,
    ) -> ReplanResult:

        base = objective.strip()

        if not diagnosis.failed:
            return ReplanResult(
                objective=base,
                strategy="initial",
                attempt=attempt,
                reason=(
                    "No validation failure requires "
                    "replanning."
                ),
            )

        learned = tuple(
            dict(item)
            for item in (learned_context or [])
            if isinstance(item, dict)
        )

        strategy = self._strategy(
            diagnosis,
            learned,
        )

        lines = [
            base,
            "",
            "AUTONOMOUS FAILURE-AWARE REPLAN",
            f"Previous attempt: {attempt}",
            f"Validation failures: {diagnosis.failed}",
            f"Replanning strategy: {strategy}",
        ]

        if diagnosis.files:
            lines.append(
                "Failed files: "
                + ", ".join(diagnosis.files)
            )

        if diagnosis.validators:
            lines.append(
                "Failed validators: "
                + ", ".join(diagnosis.validators)
            )

        if learned:
            lines.extend(
                [
                    "",
                    "RELIABLE LEARNED KNOWLEDGE",
                ]
            )

            for index, item in enumerate(
                learned,
                start=1,
            ):
                title = str(
                    item.get("title", "")
                ).strip()

                content = str(
                    item.get("content", "")
                ).strip()

                confidence = item.get(
                    "confidence",
                    0.0,
                )

                success_rate = item.get(
                    "success_rate",
                    0.0,
                )

                promoted = bool(
                    item.get(
                        "promoted",
                        False,
                    )
                )

                detail = (
                    f"{index}. "
                    + (
                        title
                        or "learned pattern"
                    )
                )

                if content:
                    detail += (
                        f": {content}"
                    )

                detail += (
                    f" [confidence={confidence}; "
                    f"success_rate={success_rate}; "
                    f"promoted={promoted}]"
                )

                lines.append(detail)

        for index, issue in enumerate(
            diagnosis.issues,
            start=1,
        ):
            validator = str(
                issue.get("validator", "")
            ).strip()

            severity = str(
                issue.get("severity", "")
            ).strip()

            message = str(
                issue.get("message", "")
            ).strip()

            file = str(
                issue.get("file", "")
            ).strip()

            line = int(
                issue.get("line", 0) or 0
            )

            column = int(
                issue.get("column", 0) or 0
            )

            suggestion = str(
                issue.get("suggestion", "")
            ).strip()

            location = (
                file or "unknown file"
            )

            if line:
                location += f":{line}"

                if column:
                    location += f":{column}"

            detail = (
                f"{index}. {location}"
            )

            if validator:
                detail += (
                    f" [{validator}]"
                )

            if severity:
                detail += (
                    f" [{severity}]"
                )

            if message:
                detail += (
                    f" {message}"
                )

            if suggestion:
                detail += (
                    " Suggestion: "
                    + suggestion
                )

            lines.append(detail)

        lines.extend(
            [
                "",
                "NEXT ATTEMPT REQUIREMENTS",
                (
                    "Re-evaluate the failed files and validation "
                    "issues before generating changes."
                ),
                (
                    "Apply reliable learned knowledge where it "
                    "directly matches the diagnosed failure."
                ),
                (
                    "Do not repeat the previous failed approach "
                    "unchanged."
                ),
                "Preserve unrelated repository behavior.",
                (
                    "Produce changes that directly address the "
                    "diagnosed validation failure."
                ),
            ]
        )

        return ReplanResult(
            objective="\n".join(lines),
            strategy=strategy,
            attempt=attempt,
            files=diagnosis.files,
            issues=diagnosis.issues,
            validators=diagnosis.validators,
            learned_context=learned,
            reason=(
                "Validation failure and reliable learned knowledge "
                "converted into failure-aware planning input."
            ),
        )

    def _strategy(
        self,
        diagnosis: FailureDiagnosis,
        learned_context: tuple[dict[str, Any], ...] = (),
    ) -> str:

        messages = " ".join(
            str(issue.get("message", "")).lower()
            for issue in diagnosis.issues
        )

        validators = {
            validator.lower()
            for validator in diagnosis.validators
        }

        has_knowledge = bool(
            learned_context
        )

        if "python" in validators:
            if (
                "syntax" in messages
                or "parse" in messages
                or "invalid" in messages
            ):
                base = "correct-python-structure"

            elif "import" in messages:
                base = "correct-python-dependency-boundary"

            else:
                base = "correct-python-validation-failure"

        elif diagnosis.files:
            base = "repair-diagnosed-files"

        else:
            base = "revise-failed-approach"

        return base


replanner = ReplanEngine()


__all__ = (
    "ReplanResult",
    "ReplanEngine",
    "replanner",
)
