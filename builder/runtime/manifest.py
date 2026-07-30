from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RuntimeManifest:
    """
    Runtime manifest describing the current Builder workspace.
    """

    name: str = "Vidhi-Builder"

    version: str = "1.0"

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    workspace: str = ""

    modules: int = 0

    files: int = 0

    packages: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

    def update(
        self,
        **values: Any,
    ) -> None:

        for key, value in values.items():

            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.metadata[key] = value

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RuntimeManifest":

        manifest = cls()

        for key, value in data.items():

            if hasattr(manifest, key):
                setattr(manifest, key, value)
            else:
                manifest.metadata[key] = value

        return manifest


