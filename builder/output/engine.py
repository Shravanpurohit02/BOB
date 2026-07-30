from datetime import datetime
from pathlib import Path
from uuid import uuid4

from builder.output.writer import writer
from builder.staging import engine as staging_engine


class OutputEngine:

    def create(
        self,
        objective: str,
        workspace: str,
        metadata: dict | None = None,
        transaction=None,
    ):

        run_id = uuid4().hex

        root = Path(".builder/output") / run_id
        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        meta = {
            "id": run_id,
            "builder_version": "0.1.0-alpha.1",
            "objective": objective,
            "workspace": workspace,
            "created_at": datetime.utcnow().isoformat(),
        }

        if metadata:
            meta.update(metadata)

        if (
            transaction is not None
            and getattr(transaction, "transaction", None) is not None
        ):
            try:
                meta["transaction"] = transaction.id
            except Exception:
                pass

        writer.write(
            root,
            "metadata.json",
            meta,
        )

        writer.write(
            root,
            "objective.md",
            objective,
        )

        latest = Path(".builder/output/latest")

        latest.mkdir(
            parents=True,
            exist_ok=True,
        )

        writer.write(
            latest,
            "latest_run.json",
            {
                "run_id": run_id,
                "path": str(root),
                "created_at": meta["created_at"],
            },
        )

        return {
            "id": run_id,
            "path": str(root),
            "metadata": meta,
        }

    def stage_generation(
        self,
        workspace: str,
        generation,
    ):

        session = staging_engine.create(
            workspace,
        )

        for directory in getattr(
            generation,
            "directories",
            [],
        ):
            staging_engine.stage_directory(
                session,
                directory.path,
            )

        for artifact in getattr(
            generation,
            "artifacts",
            [],
        ):

            for directory in artifact.directories:
                staging_engine.stage_directory(
                    session,
                    directory.path,
                )

            for file in artifact.files:
                staging_engine.stage_file(
                    session,
                    file.path,
                    file.content,
                    action=file.action,
                )

        return session

    def apply_generation(
        self,
        workspace: str,
        generation,
    ):
        """
        Compatibility wrapper.
        Stage → Commit → Return generation.
        """

        session = self.stage_generation(
            workspace,
            generation,
        )

        staging_engine.commit(
            session,
            workspace,
        )

        return generation


engine = OutputEngine()
