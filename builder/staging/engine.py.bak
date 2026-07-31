import shutil
from pathlib import Path

from builder.patch.engine import engine as patch_engine

from .models import (
    StagedDirectory,
    StagedFile,
    StagingSession,
)


class StagingEngine:

    def create(self, workspace: str):

        workspace = Path(workspace).resolve()

        root = workspace / ".builder" / "staging"

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        session = StagingSession()
        session.root = str(root / session.id)

        Path(session.root).mkdir(
            parents=True,
            exist_ok=True,
        )

        return session

    def stage_directory(
        self,
        session,
        path,
    ):
        target = Path(session.root) / path

        target.mkdir(
            parents=True,
            exist_ok=True,
        )

        session.directories.append(
            StagedDirectory(path=path)
        )

    def stage_file(
        self,
        session,
        path,
        content,
        action="create",
    ):
        source = ""

        if action != "delete":
            target = Path(session.root) / path

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            target.write_text(
                content,
                encoding="utf-8",
            )

            source = str(target)

        session.files.append(
            StagedFile(
                path=path,
                source=source,
                action=action,
            )
        )

    def commit(
        self,
        session,
        workspace,
    ):
        workspace = Path(workspace).resolve()

        committed = []

        for item in session.files:

            destination = workspace / item.path

            if item.action == "delete":

                destination.unlink(
                    missing_ok=True,
                )

                committed.append(str(destination))
                continue

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            patch_engine.apply(
                path=str(destination),
                updated=Path(item.source).read_text(
                    encoding="utf-8",
                ),
                action=item.action,
            )

            committed.append(str(destination))

        return committed

    def discard(self, session):

        shutil.rmtree(
            session.root,
            ignore_errors=True,
        )


engine = StagingEngine()
