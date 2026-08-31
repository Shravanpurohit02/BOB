from __future__ import annotations

from builder.code_library.models import (
    CodeAsset,
    CodeAssetFile,
    CodeAssetLifecycle,
    CodeAssetProvenance,
    CodeAssetType,
)
from builder.code_library.provenance import CodeLibraryProvenance
from builder.code_library.lifecycle import CodeLibraryLifecycle
from builder.code_library.retrieval import CodeLibraryRetrievalEngine
from builder.code_library.composition import (
    CodeLibraryCompositionEngine,
    CodeLibraryCompositionError,
)
from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationRequest,
)
from builder.guardrails.validators.quality import QualityValidator


NAME = "Code Library Validation & Asset Quality"
CATEGORY = "Code Library"
DESCRIPTION = (
    "Validates CL-8 asset identity, provenance, lifecycle, "
    "quality scoring, composition eligibility and guardrail quality contracts."
)


def _asset(
    *,
    lifecycle: str = CodeAssetLifecycle.PROMOTED.value,
    source: str = "cl8-regression",
    license: str = "MIT",
    content: str = "value = 1\n",
) -> CodeAsset:
    return CodeAsset(
        id="cl8-asset",
        asset_type=CodeAssetType.COMPONENT.value,
        name="CL8 Component",
        description="CL-8 validation regression asset",
        language="python",
        framework="",
        runtime="python",
        version="1.0.0",
        tags=["cl8", "validation"],
        capabilities=["testing"],
        dependencies=[],
        entrypoints=["main"],
        files=[
            CodeAssetFile(
                path="component.py",
                content=content,
                language="python",
            )
        ],
        provenance=CodeAssetProvenance(
            source=source,
            source_type="regression",
            author="BOB",
            license=license,
        ),
        lifecycle=lifecycle,
    )


def run() -> bool:
    try:
        # ------------------------------------------------------------------
        # 1. Canonical file/asset fingerprints must be deterministic.
        # ------------------------------------------------------------------
        first = _asset()
        second = _asset()

        if first.files[0].fingerprint != second.files[0].fingerprint:
            return False

        if first.fingerprint != second.fingerprint:
            return False

        if first.stable_id != second.stable_id:
            return False

        # ------------------------------------------------------------------
        # 2. Provenance validation must reject incomplete provenance.
        # ------------------------------------------------------------------
        valid, issues = CodeLibraryProvenance.validate_asset(first)

        if not valid or issues:
            return False

        invalid = _asset(
            source="",
            license="",
        )

        valid, issues = CodeLibraryProvenance.validate_asset(invalid)

        if valid:
            return False

        if "source is required" not in issues:
            return False

        if "license is required" not in issues:
            return False

        # ------------------------------------------------------------------
        # 3. Lifecycle must enforce draft -> validated -> promoted.
        # ------------------------------------------------------------------
        lifecycle_asset = _asset(
            lifecycle=CodeAssetLifecycle.DRAFT.value,
        )

        CodeLibraryLifecycle.validate(lifecycle_asset)

        if lifecycle_asset.lifecycle != CodeAssetLifecycle.VALIDATED.value:
            return False

        CodeLibraryLifecycle.promote(lifecycle_asset)

        if lifecycle_asset.lifecycle != CodeAssetLifecycle.PROMOTED.value:
            return False

        # ------------------------------------------------------------------
        # 4. Retrieval quality score must reward valid promoted assets.
        # ------------------------------------------------------------------
        retrieval = CodeLibraryRetrievalEngine()

        quality = retrieval._quality_score(first)

        if not 0.0 <= quality <= 1.0:
            return False

        if quality <= 0.0:
            return False

        # ------------------------------------------------------------------
        # 5. Composition must reject invalid provenance/lifecycle.
        # ------------------------------------------------------------------
        composition = CodeLibraryCompositionEngine()

        result = composition.compose(first)

        if result.asset_id != first.id:
            return False

        if result.asset_fingerprint != first.fingerprint:
            return False

        bad_provenance = _asset(
            source="",
            license="",
        )

        try:
            composition.compose(bad_provenance)
            return False
        except CodeLibraryCompositionError:
            pass

        draft = _asset(
            lifecycle=CodeAssetLifecycle.DRAFT.value,
        )

        try:
            composition.compose(draft)
            return False
        except CodeLibraryCompositionError:
            pass

        # ------------------------------------------------------------------
        # 6. QualityValidator must detect production-quality violations.
        # ------------------------------------------------------------------
        validator = QualityValidator()

        request = ValidationRequest(
            workspace=first.files[0].path,
            patch={
                "files": [
                    {
                        "path": "component.py",
                        "content": (
                            "# TODO: remove this\n"
                            "def main():\n"
                            "    pass\n"
                        ),
                    }
                ]
            },
        )

        report = validator.validate(
            request,
            ValidationContext(),
        )

        if report.validator != "quality":
            return False

        if not report.issues:
            return False

        codes = {
            issue.code
            for issue in report.issues
        }

        if "QUALITY001" not in codes:
            return False

        if "QUALITY002" not in codes:
            return False

        if any(
            issue.severity is not Severity.WARNING
            for issue in report.issues
        ):
            return False

        # ------------------------------------------------------------------
        # 7. Clean production code must not generate quality issues.
        # ------------------------------------------------------------------
        clean_request = ValidationRequest(
            workspace=first.files[0].path,
            patch={
                "files": [
                    {
                        "path": "component.py",
                        "content": (
                            "def main():\n"
                            "    return 1\n"
                        ),
                    }
                ]
            },
        )

        clean_report = validator.validate(
            clean_request,
            ValidationContext(),
        )

        if clean_report.issues:
            return False

        return True

    except Exception:
        return False


__all__ = (
    "NAME",
    "CATEGORY",
    "DESCRIPTION",
    "run",
)
