from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetFile, CodeAssetProvenance


@dataclass(frozen=True)
class AdminDashboardDefinition:
    """Canonical definition for a reusable admin dashboard asset."""

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
            asset_type="page",
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
                source_type="admin-dashboard",
                author="BOB",
                license="BOB-native",
                reference=self.asset_id,
            ),
            metadata={
                "admin_dashboard": True,
                "dashboard_type": "admin",
                "source": "BOB",
                **dict(self.metadata or {}),
            },
        )


class AdminDashboardRegistry:
    """Registry for reusable administrative dashboard assets."""

    SOURCE_TYPE = "admin-dashboard"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: AdminDashboardDefinition,
    ) -> CodeAsset:
        if self.engine.get(definition.asset_id) is not None:
            raise ValueError(
                f"Admin dashboard already exists: "
                f"{definition.asset_id}"
            )

        asset = definition.to_asset()

        if not self.is_dashboard(asset):
            raise ValueError(
                "Invalid admin dashboard definition"
            )

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[AdminDashboardDefinition],
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

        if asset is None or not self.is_dashboard(asset):
            return None

        return asset

    def list_dashboards(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_dashboard(asset)
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    @staticmethod
    def is_dashboard(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.asset_type == "page"
            and asset.provenance.source_type
            == AdminDashboardRegistry.SOURCE_TYPE
            and asset.metadata.get("admin_dashboard") is True
            and asset.metadata.get("dashboard_type")
            == "admin"
        )


admin_dashboards = AdminDashboardRegistry()


__all__ = (
    "AdminDashboardDefinition",
    "AdminDashboardRegistry",
    "admin_dashboards",
)
