from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetProvenance


@dataclass(frozen=True)
class BOBNativeAssetDefinition:
    """Canonical definition for a BOB-native Code Library asset."""

    asset_id: str
    name: str
    asset_type: str
    description: str = ""
    language: str = ""
    framework: str = ""
    runtime: str = ""
    version: str = "1.0.0"
    tags: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
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
            provenance=CodeAssetProvenance(
                source="BOB",
                source_type="native",
                author="BOB",
                license="BOB-native",
                reference=self.asset_id,
            ),
            metadata={
                "native": True,
                "source": "BOB",
                **dict(self.metadata or {}),
            },
        )


class BOBNativeAssetRegistry:
    """Registry for production Code Library assets authored by BOB."""

    SOURCE = "BOB"
    SOURCE_TYPE = "native"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: BOBNativeAssetDefinition,
    ) -> CodeAsset:
        existing = self.engine.get(definition.asset_id)

        if existing is not None:
            raise ValueError(
                f"BOB-native asset already exists: "
                f"{definition.asset_id}"
            )

        asset = definition.to_asset()

        if not asset.provenance.source:
            raise ValueError(
                "BOB-native asset provenance source is required"
            )

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[BOBNativeAssetDefinition],
    ) -> tuple[CodeAsset, ...]:
        registered: list[CodeAsset] = []

        for definition in definitions:
            registered.append(
                self.register(definition)
            )

        return tuple(registered)

    def get(
        self,
        asset_id: str,
    ) -> CodeAsset | None:
        asset = self.engine.get(asset_id)

        if asset is None:
            return None

        if not self.is_native(asset):
            return None

        return asset

    def list_assets(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_native(asset)
        )

    @staticmethod
    def is_native(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.provenance.source == "BOB"
            and asset.provenance.source_type == "native"
            and asset.metadata.get("native") is True
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None


native_assets = BOBNativeAssetRegistry()


__all__ = (
    "BOBNativeAssetDefinition",
    "BOBNativeAssetRegistry",
    "native_assets",
)
