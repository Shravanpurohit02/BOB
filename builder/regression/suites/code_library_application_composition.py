from __future__ import annotations

from tempfile import TemporaryDirectory

from builder.codegen.artifacts import GeneratedFile
from builder.code_library.application_composition import (
    ApplicationCompositionEngine,
    ApplicationCompositionRequest,
)
from builder.code_library.models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetLifecycle,
    CodeAssetProvenance,
)
from builder.code_library.store import CodeLibraryStore


def _asset(
    asset_id: str,
    name: str,
    files: list[tuple[str, str]],
    *,
    language: str = "python",
) -> CodeAsset:
    return CodeAsset(
        id=asset_id,
        asset_type="component",
        name=name,
        description="CL-6 application composition regression asset.",
        language=language,
        files=[
            CodeAssetFile(
                path=path,
                language=language,
                content=content,
            )
            for path, content in files
        ],
        provenance=CodeAssetProvenance(
            source=f"regression:{asset_id}",
            source_type="local_file",
            reference=f"regression:{asset_id}",
            license="MIT",
            
        ),
        lifecycle=CodeAssetLifecycle.PROMOTED.value,
    )


def run() -> bool:
    with TemporaryDirectory() as directory:
        store = CodeLibraryStore(root=directory)

        first = _asset(
            "cl6-a",
            "Application Core",
            [
                (
                    "app/core.py",
                    "VALUE = 1\n",
                ),
            ],
        )

        second = _asset(
            "cl6-b",
            "Application API",
            [
                (
                    "app/api.py",
                    "from app.core import VALUE\n",
                ),
            ],
        )

        store.save(first)
        store.save(second)

        engine = ApplicationCompositionEngine()

        # Use the same store through the retrieval engine so the test
        # validates the complete CL-4 -> CL-6 boundary.
        from builder.code_library.retrieval import (
            CodeLibraryRetrievalEngine,
        )

        engine = ApplicationCompositionEngine(
            retrieval=CodeLibraryRetrievalEngine(store=store)
        )

        result = engine.compose(
            ApplicationCompositionRequest(
                query="Application Core API",
                limit=10,
            )
        )

        if not result.success:
            return False

        if len(result.assets) != 2:
            return False

        if len(result.artifacts) != 1:
            return False

        files = result.artifacts[0].files

        if len(files) != 2:
            return False

        if [item.path for item in files] != [
            "app/api.py",
            "app/core.py",
        ]:
            return False

        if any(
            not isinstance(item, GeneratedFile)
            for item in files
        ):
            return False

        if any(
            item.action != "create"
            for item in files
        ):
            return False

        # Collision must be rejected deterministically.
        collision = _asset(
            "cl6-collision",
            "Collision",
            [
                (
                    "app/core.py",
                    "CONFLICT = True\n",
                ),
            ],
        )

        store.save(collision)

        collision_result = engine.compose(
            ApplicationCompositionRequest(
                query="Application Core Collision",
                limit=10,
            )
        )

        if collision_result.success:
            return False

        if not collision_result.errors:
            return False

        return True


DESCRIPTION = (
    "Validates CL-6 deterministic multi-asset application "
    "composition into GeneratedArtifact without filesystem mutation."
)


if __name__ == "__main__":
    print("=" * 100)
    print("BOB — CL-6 APPLICATION COMPOSITION REGRESSION")
    print("=" * 100)
    print("RESULT:", run())
    print("=" * 100)
