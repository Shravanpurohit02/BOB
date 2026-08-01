import re
from pathlib import Path

from builder.context.selector import selector
from builder.execution.task_queue import QueueTask
from builder.execution.task_queue import engine as task_queue
from builder.intelligence.impact import impact
from builder.planning.task_decomposer import engine as task_decomposer

from .engine import engine


class PlanAnalyzer:
    VERBS = (
        "delete",
        "modify",
        "update",
        "rename",
        "move",
        "create",
        "remove",
    )

    def _target(self, objective: str):

        text = objective.lower()

        for verb in self.VERBS:
            m = re.search(
                rf"{verb}\s+([A-Za-z0-9_./\\-]+\.[A-Za-z0-9_]+)",
                text,
            )

            if m:
                return m.group(1)

        m = re.search(
            r"([A-Za-z0-9_./\\-]+\.[A-Za-z0-9_]+)",
            text,
        )

        if m:
            return m.group(1)

        return objective.strip()

    def analyze(
        self,
        objective: str,
        workspace: str,
        transaction=None,
    ):

        plan = engine.create(
            objective,
            workspace=workspace,
        )

        milestone = plan.milestones[0]
        job = milestone.jobs[0]

        try:
            for task in task_decomposer.decompose(objective):
                engine.add_task(
                    job,
                    title=task.title,
                    objective=task.objective,
                )

                task_queue.add(
                    QueueTask(
                        id=task.id,
                        title=task.title,
                        objective=task.objective,
                        priority=task.priority,
                        dependencies=task.dependencies,
                    )
                )
        except Exception:
            pass

        target = self._target(objective)

        report = impact.analyze(
            workspace,
            target,
        )

        plan.impact = report

        added = set()

        for module in report.validation_scope:
            filename = module.replace(".", "/") + ".py"

            if filename not in added:
                engine.add_task(
                    job,
                    title=filename,
                    objective="Modify " + filename,
                )

                added.add(filename)

        if not added:
            for module in selector.select(
                workspace,
                objective,
            ):
                workspace_path = Path(workspace).resolve()
                module_path = Path(module.path).resolve()

                try:
                    path = module_path.relative_to(workspace_path).as_posix()
                except ValueError:
                    path = module_path.name

                if path in added:
                    continue

                engine.add_task(
                    job,
                    title=path,
                    objective="Modify " + path,
                )

                added.add(path)

        if transaction is not None:
            try:
                plan.metadata["transaction"] = transaction.id
            except Exception:
                pass

        return plan


analyzer = PlanAnalyzer()
