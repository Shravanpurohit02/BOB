from __future__ import annotations

from .models import CodeAsset, CodeAssetProvenance


class CodeLibraryProvenance:
    """
    Validates the minimum provenance contract for reusable
    application assets.

    The library never silently treats an unknown source as
    a licensed redistributable asset.
    """

    @staticmethod
    def validate(
        provenance: CodeAssetProvenance,
    ) -> tuple[bool, tuple[str, ...]]:
        issues: list[str] = []

        if not provenance.source.strip():
            issues.append("source is required")

        if not provenance.source_type.strip():
            issues.append("source_type is required")

        if not provenance.license.strip():
            issues.append("license is required")

        return (
            not issues,
            tuple(issues),
        )

    @classmethod
    def validate_asset(
        cls,
        asset: CodeAsset,
    ) -> tuple[bool, tuple[str, ...]]:
        return cls.validate(asset.provenance)


provenance = CodeLibraryProvenance()

__all__ = (
    "CodeLibraryProvenance",
    "provenance",
)
