from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetFile, CodeAssetProvenance


@dataclass(frozen=True)
class EcommerceAssetDefinition:
    """Canonical definition for a reusable e-commerce asset."""

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
                source_type="ecommerce",
                author="BOB",
                license="BOB-native",
                reference=self.asset_id,
            ),
            metadata={
                "ecommerce_asset": True,
                "business_domain": "ecommerce",
                "source": "BOB",
                **dict(self.metadata or {}),
            },
        )


class EcommerceAssetRegistry:
    """Registry for reusable e-commerce Code Library assets."""

    SOURCE_TYPE = "ecommerce"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: EcommerceAssetDefinition,
    ) -> CodeAsset:
        if self.engine.get(definition.asset_id) is not None:
            raise ValueError(
                f"E-commerce asset already exists: {definition.asset_id}"
            )

        asset = definition.to_asset()

        if not self.is_ecommerce(asset):
            raise ValueError(
                "Invalid e-commerce asset definition"
            )

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[EcommerceAssetDefinition],
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

        if asset is None or not self.is_ecommerce(asset):
            return None

        return asset

    def list_assets(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_ecommerce(asset)
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    @staticmethod
    def is_ecommerce(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.provenance.source_type
            == EcommerceAssetRegistry.SOURCE_TYPE
            and asset.metadata.get("ecommerce_asset") is True
            and asset.metadata.get("business_domain")
            == "ecommerce"
        )


ecommerce_assets = EcommerceAssetRegistry()


__all__ = (
    "EcommerceAssetDefinition",
    "EcommerceAssetRegistry",
    "ecommerce_assets",
)
