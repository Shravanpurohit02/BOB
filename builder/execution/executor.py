import time

from builder.execution.result import ExecutionResult
from builder.engineering.transaction.context import TransactionContext

from builder.planning import analyzer
from builder.planning.executor import executor as planning_executor

from builder.validation import engine as validation
from builder.testing import engine as testing

from builder.autonomous_runtime.repair import repair

from builder.engineering.changeset import engine as changesets
from builder.engineering.transaction.engine import (
    engine as transactions,
)

from builder.output import engine as output
from builder.execution.snapshot import (
    manager as snapshots,
)
from builder.execution.snapshot.recovery import (
    recovery as snapshot_recovery,
)

from builder.execution.task_queue import engine as task_queue


class Executor:

    MAX_REPAIRS = 3

    def execute(self, context):


        try:
            context.metadata["queue"] = {
                "total": len(task_queue.tasks),
                "pending": len(task_queue.pending()),
                "ready": len(task_queue.ready()),
            }
        except Exception:
            pass

        workspace = getattr(
            context,
            "workspace",
            ".",
        )

        objective = getattr(
            context,
            "objective",
            "Execution",
        )

        started = time.perf_counter()

        result = ExecutionResult()

        if (
            getattr(context, "transaction", None)
            is not None
            and getattr(
                context.transaction,
                "transaction",
                None,
            ) is not None
        ):
            transaction = context.transaction.transaction
        else:
            transaction = transactions.begin(
                objective=objective,
                workspace=workspace,
            )

            context.transaction = TransactionContext(
                transaction=transaction,
            )

        if context.snapshot is None:

            snapshot = snapshot_recovery.resume_latest()

            if (
                snapshot is not None
                and snapshot.transaction_id == transaction.id
            ):
                context.snapshot = snapshot

                context.metadata["resume_stage"] = (
                    snapshot_recovery.next_stage(
                        snapshot,
                        [
                            "changeset",
                            "output",
                            "planning",
                            "validation",
                            "testing",
                        ],
                    )
                )

            else:
                context.snapshot = snapshots.create(
                    transaction_id=transaction.id,
                    execution_id=context.id,
                    objective=objective,
                    workspace=workspace,
                )

                context.metadata["resume_stage"] = "changeset"

        snapshots.before_stage(
            context.snapshot,
            "changeset",
        )

        transactions.start_stage(
            transaction,
            "changeset",
        )

        changeset = changesets.create(
            objective=objective,
            workspace=workspace,
        )

        transactions.attach_changeset(
            transaction,
            changeset,
        )

        transactions.finish_stage(
            transaction,
            "changeset",
        )

        snapshots.after_stage(
            context.snapshot,
            "changeset",
            metadata={
                "changeset_id": changeset.id,
            },
        )

        snapshots.before_stage(
            context.snapshot,
            "output",
        )

        transactions.start_stage(
            transaction,
            "output",
        )

        artifact = output.create(
            objective=objective,
            workspace=workspace,
            metadata={
                "changeset": changeset.id,
                "transaction": transaction.id,
                "started": started,
            },
        )

        if isinstance(artifact, dict):
            result.artifacts.append(
                artifact["path"]
            )

            transactions.attach_artifact(
                transaction,
                artifact["path"],
            )

        else:

            result.artifacts.extend(
                artifact.files
            )

            for file in artifact.files:
                transactions.attach_artifact(
                    transaction,
                    file,
                )

        result.changeset = changeset.id

        transactions.finish_stage(
            transaction,
            "output",
        )

        snapshots.after_stage(
            context.snapshot,
            "output",
            metadata={
                "artifact_id": artifact["id"],
                "output_path": artifact["path"],
            },
        )

        try:

            snapshots.before_stage(
                context.snapshot,
                "planning",
            )

            transactions.start_stage(
                transaction,
                "planning",
            )

            plan = analyzer.analyze(
                objective=objective,
                workspace=workspace,
            )

            planning_executor.execute(plan)

            result.completed_stages.append(
                "planning"
            )

            transactions.finish_stage(
                transaction,
                "planning",
            )

            snapshots.after_stage(
                context.snapshot,
                "planning",
                metadata={
                    "plan_id": getattr(
                        plan,
                        "id",
                        "",
                    ),
                    "milestones": len(
                        getattr(
                            plan,
                            "milestones",
                            [],
                        )
                    ),
                },
            )

            repairs = 0

            while True:

                snapshots.before_stage(
                    context.snapshot,
                    "validation",
                )

                transactions.start_stage(
                    transaction,
                    "validation",
                )

                scope = getattr(
                    getattr(plan, "impact", None),
                    "validation_scope",
                    None,
                )

                if scope:
                    result.validation = validation.validate_files(scope)
                else:
                    result.validation = validation.validate(workspace)

                transactions.attach_validation(
                    transaction,
                    result.validation,
                )

                result.completed_stages.append(
                    "validation"
                )

                transactions.finish_stage(
                    transaction,
                    "validation",
                )

                snapshots.after_stage(
                    context.snapshot,
                    "validation",
                    metadata={
                        "attempt": repairs + 1,
                        "passed": result.validation.get("failed", 0) == 0,
                        "failed": result.validation.get("failed", 0),
                        "files": result.validation.get("files", 0),
                        "repair_count": repairs,
                        "validation_scope": bool(scope),
                    },
                )

                if result.validation.get("failed", 0) == 0:
                    break

                if repairs >= self.MAX_REPAIRS:
                    result.failed_stages.append(
                        "validation"
                    )
                    break

                transactions.start_stage(
                    transaction,
                    "repair",
                )

                kwargs = {
                    "workspace": workspace,
                    "context": {
                        "validation": result.validation,
                        "testing": result.testing,
                    },
                }

                if scope:
                    kwargs["paths"] = scope

                repair.repair(**kwargs)

                repairs += 1

                result.completed_stages.append(
                    f"repair-{repairs}"
                )

                transactions.finish_stage(
                    transaction,
                    "repair",
                )

            snapshots.before_stage(
                context.snapshot,
                "testing",
            )

            transactions.start_stage(
                transaction,
                "testing",
            )

            if scope:
                result.testing = testing.execute_files(scope)
            else:
                result.testing = testing.execute(workspace)

            transactions.attach_testing(
                transaction,
                result.testing,
            )

            result.completed_stages.append(
                "testing"
            )

            transactions.finish_stage(
                transaction,
                "testing",
            )

            snapshots.after_stage(
                context.snapshot,
                "testing",
                metadata={
                    "passed": result.testing.get("failed", 0) == 0,
                    "failed": result.testing.get("failed", 0),
                    "files": result.testing.get("files", 0),
                },
            )

            result.success = (
                result.validation.get("failed", 0) == 0
                and
                result.testing.get("failed", 0) == 0
            )

            if result.success:
                snapshots.complete(
                    context.snapshot,
                )

                changesets.complete(changeset)

            changesets.save(changeset)

            transactions.attach_execution(
                transaction,
                result,
            )

            transactions.commit(transaction)

        except Exception as exc:

            result.success = False

            result.failed_stages.append(
                type(exc).__name__
            )

            result.message = str(exc)

            snapshots.fail_stage(
                context.snapshot,
                "execution",
                str(exc),
            )

            transactions.fail(
                transaction,
                str(exc),
            )

            changesets.report(
                changeset,
                summary=str(exc),
                recommendations=[
                    "Review execution log",
                    "Run repair pipeline",
                ],
            )

            changesets.save(changeset)

        result.elapsed = round(
            time.perf_counter() - started,
            6,
        )

        if result.success and not result.message:
            result.message = "completed"

        return result


executor = Executor()