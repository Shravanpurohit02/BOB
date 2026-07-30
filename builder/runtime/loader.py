from __future__ import annotations

import json
from pathlib import Path

from builder.runtime.manifest import RuntimeManifest
from builder.runtime.runtime import Runtime


class RuntimeLoader:
    """
    Load and save Builder runtime state.
    """

    def save_runtime(
        self,
        runtime: Runtime,
        path: str | Path,
    ) -> Path:

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                runtime.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return path

    def load_runtime(
        self,
        path: str | Path,
    ) -> Runtime:

        data = json.loads(
            Path(path).read_text(
                encoding="utf-8",
            )
        )

        return Runtime.from_dict(data)

    def save_manifest(
        self,
        manifest: RuntimeManifest,
        path: str | Path,
    ) -> Path:

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                manifest.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return path

    def load_manifest(
        self,
        path: str | Path,
    ) -> RuntimeManifest:

        data = json.loads(
            Path(path).read_text(
                encoding="utf-8",
            )
        )

        return RuntimeManifest.from_dict(
            data
        )


loader = RuntimeLoader()

