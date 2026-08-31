from pathlib import Path
from tempfile import TemporaryDirectory

from builder.code_library.models import (
    CodeAsset,
    CodeAssetLifecycle,
    CodeAssetProvenance,
)
from builder.code_library.retrieval import CodeLibraryRetrievalEngine
from builder.code_library.store import CodeLibraryStore


NAME = "Code Library Retrieval"
CATEGORY = "Code Library"
DESCRIPTION = (
    "Validates CL-4 deterministic Code Library retrieval, eligibility, "
    "filtering, ranking, quality scoring and explainable results."
)


def _asset(
    asset_id: str,
    name: str,
    *,
    lifecycle: str,
    tags: list[str],
    capabilities: list[str],
    success: int = 0,
    failures: int = 0,
) -> CodeAsset:
    asset = CodeAsset(
        id=asset_id,
        asset_type="component",
        name=name,
        description=f"Reusable {name.lower()} component.",
        language="python",
        framework="fastapi",
        runtime="python3",
        tags=tags,
        capabilities=capabilities,
        dependencies=["fastapi"],
        provenance=CodeAssetProvenance(
            source="bob-native-regression",
            source_type="bob",
            author="BOB",
            license="Proprietary",
            reference="CL-4",
        ),
        lifecycle=lifecycle,
    )
    asset.usage.uses = success + failures
    asset.usage.successes = success
    asset.usage.failures = failures
    return asset


def run() -> bool:
    try:
        with TemporaryDirectory() as directory:
            store = CodeLibraryStore(Path(directory))

            promoted = _asset(
                "cl4-auth",
                "Authentication Component",
                lifecycle=CodeAssetLifecycle.PROMOTED.value,
                tags=["authentication", "security"],
                capabilities=["login", "authentication"],
                success=9,
                failures=1,
            )

            validated = _asset(
                "cl4-dashboard",
                "Dashboard Component",
                lifecycle=CodeAssetLifecycle.VALIDATED.value,
                tags=["dashboard"],
                capabilities=["dashboard"],
                success=2,
            )

            draft = _asset(
                "cl4-draft",
                "Draft Authentication",
                lifecycle=CodeAssetLifecycle.DRAFT.value,
                tags=["authentication"],
                capabilities=["authentication"],
            )

            deprecated = _asset(
                "cl4-old-auth",
                "Deprecated Authentication",
                lifecycle=CodeAssetLifecycle.DEPRECATED.value,
                tags=["authentication"],
                capabilities=["authentication"],
                success=10,
            )

            for asset in (promoted, validated, draft, deprecated):
                store.save(asset)

            engine = CodeLibraryRetrievalEngine(store)

            result = engine.search(
                "authentication login",
                limit=10,
            )

            if result.count != 1:
                return False

            item = result.records[0]

            if item.asset.id != promoted.id:
                return False

            if "authentication" not in item.matched_tokens:
                return False

            if "login" not in item.matched_tokens:
                return False

            if item.final_score <= 0:
                return False

            if "promoted" not in item.reasons:
                return False

            if "valid_provenance" not in item.reasons:
                return False

            filtered = engine.search(
                "component",
                framework="FASTAPI",
                language="PYTHON",
                limit=10,
            )

            if [x.asset.id for x in filtered.records] != [
                promoted.id,
                validated.id,
            ]:
                return False

            draft_result = engine.search(
                "authentication",
                include_draft=True,
                limit=10,
            )

            draft_ids = {x.asset.id for x in draft_result.records}

            if draft.id not in draft_ids:
                return False

            if deprecated.id in draft_ids:
                return False

            all_result = engine.search(
                "authentication",
                include_draft=True,
                include_deprecated=True,
                limit=10,
            )

            all_ids = {x.asset.id for x in all_result.records}

            if not {
                promoted.id,
                draft.id,
                deprecated.id,
            }.issubset(all_ids):
                return False

            capability_result = engine.search(
                "login",
                capability="LOGIN",
                limit=10,
            )

            if capability_result.count != 1:
                return False

            if capability_result.records[0].asset.id != promoted.id:
                return False

            empty_query = engine.search(
                "",
                limit=2,
            )

            if empty_query.count != 2:
                return False

            return True

    except Exception:
        return False
