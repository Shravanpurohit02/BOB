from pathlib import Path
from tempfile import TemporaryDirectory

from builder.code_library.engine import CodeLibraryEngine
from builder.code_library.models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetLifecycle,
    CodeAssetProvenance,
    CodeAssetType,
)
from builder.code_library.store import CodeLibraryStore


NAME = "Code Library Foundation"
CATEGORY = "Code Library"
DESCRIPTION = (
    "Validates CL-1 canonical asset contracts, persistence, "
    "provenance, lifecycle and usage accounting."
)


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = CodeLibraryStore(
                Path(directory)
            )
            library = CodeLibraryEngine(store)

            asset = CodeAsset(
                id="cl1-application-crm",
                asset_type=CodeAssetType.APPLICATION.value,
                name="CRM Application Template",
                description=(
                    "Reusable CRM application foundation."
                ),
                language="python",
                framework="fastapi",
                runtime="python3",
                version="1.0.0",
                tags=[
                    "crm",
                    "application",
                    "template",
                ],
                capabilities=[
                    "authentication",
                    "contacts",
                    "dashboard",
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
                    reference="CL-1",
                ),
            )

            registered = library.register(asset)

            stored = library.get(
                "cl1-application-crm"
            )

            if stored is None:
                return False

            fingerprint = stored.fingerprint

            if not fingerprint:
                return False

            if stored.stable_id == "":
                return False

            if stored.lifecycle != (
                CodeAssetLifecycle.DRAFT.value
            ):
                return False

            validated = library.validate(
                stored.id
            )

            if validated.lifecycle != (
                CodeAssetLifecycle.VALIDATED.value
            ):
                return False

            promoted = library.promote(
                stored.id
            )

            if promoted.lifecycle != (
                CodeAssetLifecycle.PROMOTED.value
            ):
                return False

            library.record_use(
                stored.id,
                success=True,
            )

            library.record_use(
                stored.id,
                success=True,
            )

            final = library.get(
                stored.id
            )

            if final is None:
                return False

            return (
                registered.id
                == "cl1-application-crm"
                and final.asset_type
                == CodeAssetType.APPLICATION.value
                and final.fingerprint
                == fingerprint
                and final.lifecycle
                == CodeAssetLifecycle.PROMOTED.value
                and final.usage.uses == 2
                and final.usage.successes == 2
                and final.usage.failures == 0
                and final.success_rate == 1.0
                and store.count() == 1
            )

    except Exception:
        return False
