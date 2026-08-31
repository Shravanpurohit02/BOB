from pathlib import Path
from tempfile import TemporaryDirectory

from builder.code_library.catalog import (
    CodeLibraryCatalogEngine,
)
from builder.code_library.models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetLifecycle,
    CodeAssetProvenance,
    CodeAssetType,
)
from builder.code_library.store import CodeLibraryStore


NAME = "Code Library Catalog"
CATEGORY = "Code Library"
DESCRIPTION = (
    "Validates deterministic CL-2 catalog construction, "
    "technology organization and asset filtering."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = CodeLibraryStore(Path(directory))

            first = CodeAsset(
                id="cl2-crm-app",
                asset_type=CodeAssetType.APPLICATION.value,
                name="CRM Application",
                description="Reusable CRM application.",
                language="python",
                framework="fastapi",
                runtime="python3",
                version="1.0.0",
                tags=[
                    "CRM",
                    "Application",
                    "Template",
                ],
                capabilities=[
                    "authentication",
                    "dashboard",
                ],
                dependencies=[
                    "fastapi",
                    "pydantic",
                ],
                entrypoints=[
                    "backend/main.py",
                ],
                files=[
                    CodeAssetFile(
                        path="backend/main.py",
                        content=(
                            "from fastapi import FastAPI\n"
                            "app = FastAPI()\n"
                        ),
                        language="python",
                    ),
                ],
                provenance=CodeAssetProvenance(
                    source="bob-native-regression",
                    source_type="bob",
                    author="BOB",
                    license="Proprietary",
                    reference="CL-2",
                ),
                lifecycle=CodeAssetLifecycle.PROMOTED.value,
            )

            second = CodeAsset(
                id="cl2-dashboard-page",
                asset_type=CodeAssetType.PAGE.value,
                name="Dashboard Page",
                language="typescript",
                framework="react",
                runtime="node",
                version="2.0.0",
                tags=[
                    "dashboard",
                    "page",
                ],
                capabilities=[
                    "dashboard",
                ],
                dependencies=[
                    "react",
                ],
                provenance=CodeAssetProvenance(
                    source="bob-native-regression",
                    source_type="bob",
                    author="BOB",
                    license="Proprietary",
                    reference="CL-2",
                ),
                lifecycle=CodeAssetLifecycle.VALIDATED.value,
            )

            third = CodeAsset(
                id="cl2-auth-component",
                asset_type=CodeAssetType.COMPONENT.value,
                name="Authentication Component",
                language="typescript",
                framework="react",
                runtime="node",
                version="1.0.0",
                tags=[
                    "authentication",
                    "component",
                ],
                capabilities=[
                    "authentication",
                ],
                dependencies=[
                    "react",
                ],
                provenance=CodeAssetProvenance(
                    source="bob-native-regression",
                    source_type="bob",
                    author="BOB",
                    license="Proprietary",
                    reference="CL-2",
                ),
                lifecycle=CodeAssetLifecycle.DRAFT.value,
            )

            store.save(first)
            store.save(second)
            store.save(third)

            engine = CodeLibraryCatalogEngine(store)

            result = engine.catalog()

            if result.total != 3:
                return False

            if result.by_type != {
                "application": 1,
                "component": 1,
                "page": 1,
            }:
                return False

            if result.by_language != {
                "python": 1,
                "typescript": 2,
            }:
                return False

            if result.by_framework != {
                "fastapi": 1,
                "react": 2,
            }:
                return False

            if result.by_runtime != {
                "node": 2,
                "python3": 1,
            }:
                return False

            if result.by_lifecycle != {
                "draft": 1,
                "promoted": 1,
                "validated": 1,
            }:
                return False

            if result.by_tag["dashboard"] != 1:
                return False

            if result.by_capability["authentication"] != 2:
                return False

            python_assets = engine.list(
                language="PYTHON",
            )

            if len(python_assets) != 1:
                return False

            if python_assets[0].id != first.id:
                return False

            react_assets = engine.list(
                framework="React",
            )

            if [asset.id for asset in react_assets] != [
                third.id,
                second.id,
            ]:
                return False

            dashboard_assets = engine.list(
                tag="DASHBOARD",
            )

            if len(dashboard_assets) != 1:
                return False

            if dashboard_assets[0].id != second.id:
                return False

            authentication_assets = engine.list(
                capability="AUTHENTICATION",
            )

            if len(authentication_assets) != 2:
                return False

            dependency_assets = engine.list(
                dependency="FASTAPI",
            )

            if len(dependency_assets) != 1:
                return False

            if dependency_assets[0].id != first.id:
                return False

            promoted = engine.list(
                lifecycle="PROMOTED",
            )

            if len(promoted) != 1:
                return False

            if promoted[0].id != first.id:
                return False

            entry = engine.get(first.id)

            if entry is None:
                return False

            if entry.asset_id != first.id:
                return False

            if entry.stable_id != first.stable_id:
                return False

            if entry.fingerprint != first.fingerprint:
                return False

            if entry.asset_type != "application":
                return False

            if entry.framework != "fastapi":
                return False

            categories = engine.categories()

            return (
                categories["asset_type"]["application"] == 1
                and categories["language"]["python"] == 1
                and categories["framework"]["react"] == 2
                and categories["tag"]["template"] == 1
                and categories["capability"]["dashboard"] == 2
            )

    except Exception:
        return False
