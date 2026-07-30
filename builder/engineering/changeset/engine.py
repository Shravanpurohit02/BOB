from dataclasses import asdict
from pathlib import Path

from builder.engineering.context import inspector
from builder.engineering.state import engine as state

from .models import EngineeringChangeSet, ChangeFile
from .repository import RepositoryAnalysis
from .report import EngineeringReport
from .risk import Risk
from .storage import storage


class EngineeringEngine:

    def create(
        self,
        objective: str,
        workspace: str = "",
    ):

        ecs = EngineeringChangeSet(
            objective=objective,
        )

        if workspace:

            ctx = inspector.inspect(
                objective=objective,
                workspace=workspace,
            )

            root = Path(workspace)

            packages = {
                ".".join(parts[:i])
                for module in ctx.target_modules
                for parts in [module.split(".")]
                for i in range(1, len(parts))
            }

            ecs.repository = RepositoryAnalysis(
                project=root.name,
                python_files=len(ctx.related_files),
                packages=len(packages),
                modules=ctx.target_modules,
                dependencies=ctx.dependencies,
                entrypoints=[],
            )

        state.activate(
            ecs.id,
            objective,
        )

        return ecs

    def load(self, changeset_id):
        return storage.load(changeset_id)

    def list(self):
        return storage.all()

    def save(self, ecs):
        return storage.save(asdict(ecs))

    def complete(self, ecs):
        ecs.status = "completed"
        state.complete(ecs.id)
        self.save(ecs)

    def fail(self, ecs):
        ecs.status = "failed"
        state.fail(ecs.id)
        self.save(ecs)

    def add_file(self, ecs, path, action, reason=""):
        ecs.files.append(
            ChangeFile(
                path=path,
                action=action,
                reason=reason,
            )
        )
        return ecs

    def add_risk(
        self,
        ecs,
        severity,
        title,
        description,
        mitigation="",
    ):
        ecs.risks.append(
            Risk(
                severity=severity,
                title=title,
                description=description,
                mitigation=mitigation,
            )
        )
        return ecs

    def report(
        self,
        ecs,
        summary,
        recommendations=None,
        notes=None,
    ):
        ecs.report = EngineeringReport(
            summary=summary,
            recommendations=recommendations or [],
            notes=notes or [],
        )
        return ecs


engine = EngineeringEngine()
