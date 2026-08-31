from __future__ import annotations

import tempfile
from pathlib import Path

from builder.code_library.engine import CodeLibraryEngine
from builder.code_library.ingestion import CodeLibraryIngestion
from builder.code_library.store import CodeLibraryStore


NAME = "Code Library Ingestion"
DESCRIPTION = (
    "Validates CL-3 file and workspace ingestion, structural extraction, "
    "dependency metadata, persistence and duplicate protection."
)


def run() -> bool:
    with tempfile.TemporaryDirectory(prefix="bob-cl3-") as temporary:
        root = Path(temporary)

        source = root / "service.py"
        source.write_text(
            'import json\n'
            '\n'
            'class Service:\n'
            '    def execute(self):\n'
            '        return json.dumps({"ok": True})\n'
            '\n'
            'def create_service():\n'
            '    return Service()\n',
            encoding="utf-8",
        )

        store = CodeLibraryStore(root / "library")
        engine = CodeLibraryEngine(store)
        ingestion = CodeLibraryIngestion(engine)

        asset = ingestion.ingest_file(
            str(source),
            name="Service Component",
        )

        if asset.asset_type != "component":
            return False

        if asset.name != "Service Component":
            return False

        if not asset.files:
            return False

        if "json" not in asset.dependencies:
            return False

        if "Service" not in asset.capabilities:
            return False

        if "create_service" not in asset.capabilities:
            return False

        if asset.provenance.source_type != "local_file":
            return False

        if not store.exists(asset.id):
            return False

        if engine.get(asset.id) is None:
            return False

        try:
            ingestion.ingest_file(
                str(source),
                name="Service Component",
            )
        except ValueError:
            pass
        else:
            return False

        workspace = root / "application"
        package = workspace / "app"
        package.mkdir(parents=True)

        (package / "__init__.py").write_text(
            "",
            encoding="utf-8",
        )

        (package / "models.py").write_text(
            "class User:\n"
            "    pass\n",
            encoding="utf-8",
        )

        (package / "api.py").write_text(
            "from app.models import User\n"
            "\n"
            "def get_user() -> User:\n"
            "    return User()\n",
            encoding="utf-8",
        )

        workspace_store = CodeLibraryStore(root / "workspace-library")
        workspace_engine = CodeLibraryEngine(workspace_store)
        workspace_ingestion = CodeLibraryIngestion(workspace_engine)

        application = workspace_ingestion.ingest_workspace(
            str(workspace),
            name="Test Application",
        )

        if application.asset_type != "application":
            return False

        if application.name != "Test Application":
            return False

        if len(application.files) < 3:
            return False

        if application.metadata.get("ingestion") != "workspace":
            return False

        if application.metadata.get("python_file_count", 0) < 3:
            return False

        if application.metadata.get("module_count", 0) < 3:
            return False

        if "User" not in application.capabilities:
            return False

        if "get_user" not in application.capabilities:
            return False

        if not application.dependencies:
            return False

        if not workspace_store.exists(application.id):
            return False

        return True
