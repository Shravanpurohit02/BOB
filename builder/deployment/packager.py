from pathlib import Path
import tarfile

class Packager:

    def build(self, workspace: str):

        workspace = Path(workspace)
        output = workspace / "dist"

        output.mkdir(exist_ok=True)

        archive = output / f"{workspace.name}.tar.gz"

        with tarfile.open(archive, "w:gz") as tar:
            tar.add(
                workspace,
                arcname=workspace.name,
                filter=lambda info: None if "/dist/" in info.name else info,
            )

        return archive

packager = Packager()
