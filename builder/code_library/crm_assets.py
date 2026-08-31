from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetFile, CodeAssetProvenance


@dataclass(frozen=True)
class CRMAssetDefinition:
    """Canonical definition for a reusable CRM asset."""

    asset_id: str
    name: str
    asset_type: str = "application"
    description: str = ""
    language: str = ""
    framework: str = ""
    runtime: str = ""
    version: str = "1.0.0"
    tags: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    files: tuple[CodeAssetFile, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_asset(self) -> CodeAsset:
        return CodeAsset(
            id=self.asset_id,
            asset_type=self.asset_type,
            name=self.name,
            description=self.description,
            language=self.language,
            framework=self.framework,
            runtime=self.runtime,
            version=self.version,
            tags=list(self.tags),
            capabilities=list(self.capabilities),
            dependencies=list(self.dependencies),
            files=list(self.files),
            provenance=CodeAssetProvenance(
                source="BOB",
                source_type="crm",
                author="BOB",
                license="BOB-native",
                reference=self.asset_id,
            ),
            metadata={
                "crm_asset": True,
                "business_domain": "crm",
                "source": "BOB",
                **dict(self.metadata or {}),
            },
        )


class CRMAssetRegistry:
    """Registry for reusable CRM Code Library assets."""

    SOURCE_TYPE = "crm"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: CRMAssetDefinition,
    ) -> CodeAsset:
        if self.engine.get(definition.asset_id) is not None:
            raise ValueError(
                f"CRM asset already exists: {definition.asset_id}"
            )

        asset = definition.to_asset()

        if not self.is_crm(asset):
            raise ValueError("Invalid CRM asset definition")

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[CRMAssetDefinition],
    ) -> tuple[CodeAsset, ...]:
        return tuple(
            self.register(definition)
            for definition in definitions
        )

    def get(
        self,
        asset_id: str,
    ) -> CodeAsset | None:
        asset = self.engine.get(asset_id)

        if asset is None or not self.is_crm(asset):
            return None

        return asset

    def list_assets(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_crm(asset)
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    @staticmethod
    def is_crm(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.provenance.source_type
            == CRMAssetRegistry.SOURCE_TYPE
            and asset.metadata.get("crm_asset") is True
            and asset.metadata.get("business_domain") == "crm"
        )


crm_assets = CRMAssetRegistry()


__all__ = (
    "CRMAssetDefinition",
    "CRMAssetRegistry",
    "crm_assets",
)
