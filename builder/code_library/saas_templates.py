from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetFile, CodeAssetProvenance


@dataclass(frozen=True)
class SaaSTemplateDefinition:
    """Canonical definition for a reusable SaaS application template."""

    asset_id: str
    name: str
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
            asset_type="application",
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
                source_type="saas-template",
                author="BOB",
                license="BOB-native",
                reference=self.asset_id,
            ),
            metadata={
                "saas_template": True,
                "template_type": "saas",
                "source": "BOB",
                **dict(self.metadata or {}),
            },
        )


class SaaSTemplateRegistry:
    """Registry for reusable SaaS-level Code Library templates."""

    SOURCE_TYPE = "saas-template"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: SaaSTemplateDefinition,
    ) -> CodeAsset:
        if self.engine.get(definition.asset_id) is not None:
            raise ValueError(
                f"SaaS template already exists: "
                f"{definition.asset_id}"
            )

        asset = definition.to_asset()

        if not self.is_template(asset):
            raise ValueError(
                "Invalid SaaS template definition"
            )

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[SaaSTemplateDefinition],
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

        if asset is None or not self.is_template(asset):
            return None

        return asset

    def list_templates(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_template(asset)
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    @staticmethod
    def is_template(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.asset_type == "application"
            and asset.provenance.source_type
            == SaaSTemplateRegistry.SOURCE_TYPE
            and asset.metadata.get("saas_template") is True
            and asset.metadata.get("template_type")
            == "saas"
        )


saas_templates = SaaSTemplateRegistry()


__all__ = (
    "SaaSTemplateDefinition",
    "SaaSTemplateRegistry",
    "saas_templates",
)
