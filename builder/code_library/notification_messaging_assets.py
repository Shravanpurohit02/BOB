from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetFile, CodeAssetProvenance


@dataclass(frozen=True)
class NotificationMessagingAssetDefinition:
    """Canonical definition for a reusable notification/messaging asset."""

    asset_id: str
    name: str
    asset_type: str = "component"
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
                source_type="notification-messaging",
                author="BOB",
                license="BOB-native",
                reference=self.asset_id,
            ),
            metadata={
                "notification_messaging_asset": True,
                "communication_domain": "notification-messaging",
                "source": "BOB",
                **dict(self.metadata or {}),
            },
        )


class NotificationMessagingAssetRegistry:
    """Registry for reusable notification and messaging assets."""

    SOURCE_TYPE = "notification-messaging"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: NotificationMessagingAssetDefinition,
    ) -> CodeAsset:
        if self.engine.get(definition.asset_id) is not None:
            raise ValueError(
                f"Notification/messaging asset already exists: "
                f"{definition.asset_id}"
            )

        asset = definition.to_asset()

        if not self.is_notification_messaging(asset):
            raise ValueError(
                "Invalid notification/messaging asset definition"
            )

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[NotificationMessagingAssetDefinition],
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

        if asset is None or not self.is_notification_messaging(asset):
            return None

        return asset

    def list_assets(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_notification_messaging(asset)
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    @staticmethod
    def is_notification_messaging(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.provenance.source_type
            == NotificationMessagingAssetRegistry.SOURCE_TYPE
            and asset.metadata.get("notification_messaging_asset") is True
            and asset.metadata.get("communication_domain")
            == "notification-messaging"
        )


notification_messaging_assets = NotificationMessagingAssetRegistry()


__all__ = (
    "NotificationMessagingAssetDefinition",
    "NotificationMessagingAssetRegistry",
    "notification_messaging_assets",
)
