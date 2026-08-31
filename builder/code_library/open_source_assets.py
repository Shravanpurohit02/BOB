from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetProvenance


@dataclass(frozen=True)
class OpenSourceAssetDefinition:
    """Canonical definition for an open-source Code Library asset."""

    asset_id: str
    name: str
    asset_type: str
    source: str
    source_type: str = "open-source"
    author: str = ""
    license: str = ""
    license_url: str = ""
    attribution: str = ""
    reference: str = ""
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
        if not self.source.strip():
            raise ValueError("Open-source asset source is required")

        if not self.license.strip():
            raise ValueError("Open-source asset license is required")

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
                source=self.source,
                source_type=self.source_type,
                author=self.author,
                license=self.license,
                license_url=self.license_url,
                attribution=self.attribution,
                reference=self.reference or self.source,
            ),
            metadata={
                "open_source": True,
                "source": self.source,
                "license": self.license,
                **dict(self.metadata or {}),
            },
        )


class OpenSourceAssetRegistry:
    """Registry for externally sourced open-source Code Library assets."""

    SOURCE_TYPE = "open-source"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: OpenSourceAssetDefinition,
    ) -> CodeAsset:
        if self.engine.get(definition.asset_id) is not None:
            raise ValueError(
                f"Open-source asset already exists: "
                f"{definition.asset_id}"
            )

        asset = definition.to_asset()

        if asset.provenance.source_type != self.SOURCE_TYPE:
            raise ValueError(
                "Invalid open-source asset source type"
            )

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[OpenSourceAssetDefinition],
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

        if asset is None or not self.is_open_source(asset):
            return None

        return asset

    def list_assets(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_open_source(asset)
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    @staticmethod
    def is_open_source(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.provenance.source_type
            == OpenSourceAssetRegistry.SOURCE_TYPE
            and bool(asset.provenance.source.strip())
            and bool(asset.provenance.license.strip())
            and asset.metadata.get("open_source") is True
        )


open_source_assets = OpenSourceAssetRegistry()


__all__ = (
    "OpenSourceAssetDefinition",
    "OpenSourceAssetRegistry",
    "open_source_assets",
)
