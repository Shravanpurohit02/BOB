from __future__ import annotations

from tempfile import TemporaryDirectory
from pathlib import Path

from builder.codegen.artifacts import GeneratedArtifact
from builder.code_library.composition import (
    CodeLibraryCompositionEngine,
    CodeLibraryCompositionError,
)
from builder.code_library.models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetLifecycle,
    CodeAssetProvenance,
    CodeAssetType,
)


DESCRIPTION = (
    "Validates deterministic Code Library asset composition into "
    "the canonical GeneratedArtifact contract."
)


def _asset() -> CodeAsset:
    return CodeAsset(
        id="cl5-demo",
        asset_type=CodeAssetType.COMPONENT.value,
        name="CL-5 Template",
        description="Production composition regression asset.",
        language="python",
        framework="stdlib",
        runtime="python",
        version="2.1.0",
        tags=["template", "composition"],
        capabilities=["service"],
        dependencies=["json"],
        entrypoints=["main.py"],
        files=[
            CodeAssetFile(
                path="src/{{module}}/main.py",
                language="python",
                content=(
                    "NAME = '{{name}}'\n"
                    "MODULE = '{{module}}'\n"
                ),
            ),
            CodeAssetFile(
                path="src/{{module}}/config.json",
                language="json",
                content='{"name": "{{name}}"}\n',
            ),
        ],
        provenance=CodeAssetProvenance(
            source="cl5-regression",
            source_type="test_asset",
            license="MIT",
        ),
        lifecycle=CodeAssetLifecycle.PROMOTED.value,
    )


def run() -> bool:
    engine = CodeLibraryCompositionEngine()

    asset = _asset()

    result = engine.compose(
        asset,
        {
            "module": "demo",
            "name": "BOB",
        },
        destination="generated",
    )

    if not isinstance(result.artifact, GeneratedArtifact):
        return False

    if result.asset_id != asset.id:
        return False

    if result.asset_version != asset.version:
        return False

    if result.asset_fingerprint != asset.fingerprint:
        return False

    if result.files != (
        "generated/src/demo/main.py",
        "generated/src/demo/config.json",
    ):
        return False

    if result.artifact.files[0].action != "create":
        return False

    if "NAME = 'BOB'" not in result.artifact.files[0].content:
        return False

    if "MODULE = 'demo'" not in result.artifact.files[0].content:
        return False

    if result.artifact.files[1].content != (
        '{"name": "BOB"}\n'
    ):
        return False

    if result.substitutions != ("module", "name"):
        return False

    if not result.artifact.directories:
        return False

    # Missing variables must fail closed.
    try:
        engine.compose(
            asset,
            {"module": "demo"},
        )
    except CodeLibraryCompositionError:
        pass
    else:
        return False

    # Traversal must fail closed.
    unsafe = CodeAsset(
        id="unsafe",
        asset_type="component",
        name="Unsafe",
        files=[
            CodeAssetFile(
                path="../escape.py",
                content="print('x')",
            )
        ],
        provenance=CodeAssetProvenance(
            source="test",
            source_type="test_asset",
            license="MIT",
        ),
        lifecycle=CodeAssetLifecycle.PROMOTED.value,
    )

    try:
        engine.compose(unsafe)
    except CodeLibraryCompositionError:
        pass
    else:
        return False

    # Draft assets must never become executable composition input.
    draft = _asset()
    draft.lifecycle = CodeAssetLifecycle.DRAFT.value

    try:
        engine.compose(draft, {"module": "demo", "name": "BOB"})
    except CodeLibraryCompositionError:
        pass
    else:
        return False

    return True
