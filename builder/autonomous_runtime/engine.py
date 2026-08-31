from __future__ import annotations

import json
from pathlib import Path

from builder.config import settings
from builder.engineering.transaction.engine import engine as transactions
from builder.pipeline import engine as pipeline
from builder.review import engine as review
from builder.self_improvement import engine as improvement

from .decision import decision
from .diagnosis import diagnosis
from .history import history
from .metrics import metrics
from .models import RuntimeContext, RuntimeResult
from .repair import repair
from .replan import replanner
from builder.knowledge.core import learning as knowledge_learning
from builder.knowledge.decision import decision as knowledge_decision


class AutonomousRuntime:

    MAX_ATTEMPTS = 3

    def execute(
        self,
        objective: str,
        workspace: str,
    ):
        history.clear()

        ctx = RuntimeContext(
            objective=objective,
            workspace=workspace,
        )

        result = RuntimeResult(
            context=ctx,
        )

        transaction = transactions.begin(
            objective=objective,
            workspace=workspace,
        )

        current_objective = objective

        while ctx.attempts < self.MAX_ATTEMPTS:

            ctx.attempts += 1

            ctx.metadata["current_objective"] = current_objective

            ctx.pipeline = pipeline.start(
                current_objective,
                workspace,
            )

            for stage in ctx.pipeline.stages:
                history.add(stage)
                result.history.append(stage)

            validation = (
                ctx.pipeline.context.validation
                or {}
            )

            failure = diagnosis.diagnose(
                validation,
            )

            ctx.metadata["diagnosis"] = {
                "failed": failure.failed,
                "files": list(failure.files),
                "issues": list(failure.issues),
                "validators": list(failure.validators),
            }

            learned_context = []

            if failure.failed:
                for issue in failure.issues:
                    message = str(
                        issue.get("message", "")
                    ).strip()

                    if not message:
                        continue

                    learned = knowledge_learning.search(
                        message,
                        limit=5,
                        verified_only=True,
                    )

                    selected = knowledge_decision.select(
                        learned
                    )

                    for item in selected.records:
                        context_item = {
                            "id": item["id"],
                            "title": item["title"],
                            "content": item["content"],
                            "confidence": item["confidence"],
                            "success_rate": item["success_rate"],
                            "category": item["category"],
                            "promoted": item["promoted"],
                        }

                        if context_item not in learned_context:
                            learned_context.append(
                                context_item
                            )

                    ctx.metadata["knowledge_decision"] = {
                        "count": selected.count,
                        "reliable": selected.reliable,
                        "strategy": selected.strategy,
                    }

                ctx.metadata["learned_context"] = (
                    list(learned_context)
                )

                replanned = replanner.replan(
                    objective=objective,
                    diagnosis=failure,
                    attempt=ctx.attempts,
                    learned_context=learned_context,
                )

                current_objective = replanned.objective

                ctx.metadata["replan"] = (
                    replanned.as_metadata()
                )

                history.add("replan")
                result.history.append("replan")

            validation_passed = (
                failure.failed == 0
            )

            try:
                learning_title = (
                    "Autonomous execution success"
                    if validation_passed
                    else "Autonomous execution failure"
                )

                learning_content = (
                    "Autonomous execution completed with "
                    "validation success."
                    if validation_passed
                    else (
                        "Autonomous execution produced validation "
                        "failures: "
                        + " ".join(
                            str(issue.get("message", ""))
                            for issue in failure.issues
                        )
                    )
                )

                learning_learning = (
                    knowledge_learning.learn_from_validated_result(
                        category="autonomous-execution",
                        title=learning_title,
                        content=learning_content,
                        source="autonomous_runtime",
                        validator=(
                            ", ".join(failure.validators)
                            if failure.validators
                            else "runtime"
                        ),
                        passed=validation_passed,
                        workspace=workspace,
                        tags=[
                            "autonomous",
                            "execution",
                            "validation",
                        ],
                    )
                )

                ctx.metadata["learned_record"] = {
                    "id": learning_learning.id,
                    "title": learning_learning.title,
                    "confidence": learning_learning.confidence,
                    "successes": learning_learning.successes,
                    "failures": learning_learning.failures,
                    "promoted": learning_learning.promoted,
                }

            except Exception as exc:
                ctx.metadata["learning_error"] = str(exc)

            improvements = improvement.inspect(
                workspace,
            )

            ctx.metadata["improvements"] = len(
                improvements
            )

            review_tasks = []

            if improvements:
                out = (
                    settings.resolve_output_directory()
                    / "latest"
                )

                out.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                for item in improvements:
                    task = review.submit(item)
                    review_tasks.append(task.id)

                Path(
                    out / "improvements.json"
                ).write_text(
                    json.dumps(
                        [
                            {
                                "target": i.target,
                                "issue": i.issue,
                                "proposal": i.proposal,
                                "priority": i.priority,
                            }
                            for i in improvements
                        ],
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                ctx.metadata[
                    "review_tasks"
                ] = review_tasks

                history.add("review_queue")
                result.history.append(
                    "review_queue"
                )

            action = decision.decide(result)

            history.add(action)
            result.history.append(action)

            if action == "complete":
                result.success = True
                result.completed = True
                break

            repair_context = failure.as_context(
                objective=objective,
                workspace=workspace,
            )

            repair_context["learned_context"] = (
                list(learned_context)
            )

            repair_context["knowledge_count"] = (
                len(learned_context)
            )

            repair_context["knowledge_strategy"] = (
                ctx.metadata.get(
                    "knowledge_decision",
                    {},
                ).get(
                    "strategy",
                    "standard_repair",
                )
            )

            repair_result = repair.repair(
                workspace,
                paths=list(failure.files),
                context=repair_context,
            )

            ctx.metadata[
                "last_repair"
            ] = repair_result

            if not result.history or result.history[-1] != "repair":
                history.add("repair")
                result.history.append("repair")

            if not repair_result.get(
                "success",
                False,
            ):
                break

        transactions.commit(transaction)

        ctx.metadata["transaction"] = transaction.id
        ctx.metadata["events"] = len(
            history.all()
        )
        ctx.metadata["metrics"] = metrics.collect(
            result
        )

        return result


engine = AutonomousRuntime()
