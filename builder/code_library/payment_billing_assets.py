from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .engine import CodeLibraryEngine
from .models import CodeAsset, CodeAssetFile, CodeAssetProvenance


@dataclass(frozen=True)
class PaymentBillingAssetDefinition:
    """Canonical definition for a reusable payment/billing asset."""

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
                source_type="payment-billing",
                author="BOB",
                license="BOB-native",
                reference=self.asset_id,
            ),
            metadata={
                "payment_billing_asset": True,
                "financial_domain": "payment-billing",
                "source": "BOB",
                **dict(self.metadata or {}),
            },
        )


class PaymentBillingAssetRegistry:
    """Registry for reusable payment and billing Code Library assets."""

    SOURCE_TYPE = "payment-billing"

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def register(
        self,
        definition: PaymentBillingAssetDefinition,
    ) -> CodeAsset:
        if self.engine.get(definition.asset_id) is not None:
            raise ValueError(
                f"Payment/billing asset already exists: "
                f"{definition.asset_id}"
            )

        asset = definition.to_asset()

        if not self.is_payment_billing(asset):
            raise ValueError(
                "Invalid payment/billing asset definition"
            )

        return self.engine.register(asset)

    def register_many(
        self,
        definitions: Iterable[PaymentBillingAssetDefinition],
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

        if asset is None or not self.is_payment_billing(asset):
            return None

        return asset

    def list_assets(self) -> tuple[CodeAsset, ...]:
        return tuple(
            asset
            for asset in self.engine.list_assets()
            if self.is_payment_billing(asset)
        )

    def contains(
        self,
        asset_id: str,
    ) -> bool:
        return self.get(asset_id) is not None

    @staticmethod
    def is_payment_billing(
        asset: CodeAsset,
    ) -> bool:
        return (
            asset.provenance.source_type
            == PaymentBillingAssetRegistry.SOURCE_TYPE
            and asset.metadata.get("payment_billing_asset") is True
            and asset.metadata.get("financial_domain")
            == "payment-billing"
        )


payment_billing_assets = PaymentBillingAssetRegistry()


__all__ = (
    "PaymentBillingAssetDefinition",
    "PaymentBillingAssetRegistry",
    "payment_billing_assets",
)
