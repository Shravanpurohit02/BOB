import json
from pathlib import Path

from .models import RuntimeContext, RuntimeResult
from .decision import decision
from .repair import repair
from .history import history
from .metrics import metrics

from builder.pipeline import engine as pipeline
from builder.self_improvement import engine as improvement
from builder.review import engine as review
from builder.engineering.transaction.engine import engine as transactions


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

        while ctx.attempts < self.MAX_ATTEMPTS:

            ctx.attempts += 1

            ctx.pipeline = pipeline.start(
                objective,
                workspace,
            )

            for stage in ctx.pipeline.stages:
                history.add(stage)
                result.history.append(stage)

            improvements = improvement.inspect(
                workspace,
            )

            ctx.metadata["improvements"] = len(improvements)

            review_tasks = []

            if improvements:

                out = Path(".builder/output") / "latest"
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

                ctx.metadata["review_tasks"] = review_tasks

                history.add("review_queue")
                result.history.append("review_queue")

            action = decision.decide(result)

            history.add(action)
            result.history.append(action)

            if action == "complete":
                result.success = True
                result.completed = True
                break

            repair_result = repair.repair(workspace)

            history.add("repair")
            result.history.append("repair")

            if not repair_result.get(
                "success",
                False,
            ):
                break

        transactions.commit(transaction)

        ctx.metadata["transaction"] = transaction.id
        ctx.metadata["events"] = len(history.all())
        ctx.metadata["metrics"] = metrics.collect(result)

        return result


engine = AutonomousRuntime()
