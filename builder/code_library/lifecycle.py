from __future__ import annotations

from .models import CodeAsset, CodeAssetLifecycle


class CodeLibraryLifecycle:
    """
    Deterministic lifecycle transitions for Code Library assets.

    Assets begin as draft and must be validated before promotion.
    """

    _ALLOWED = {
        CodeAssetLifecycle.DRAFT.value: {
            CodeAssetLifecycle.DRAFT.value,
            CodeAssetLifecycle.VALIDATED.value,
            CodeAssetLifecycle.DEPRECATED.value,
        },
        CodeAssetLifecycle.VALIDATED.value: {
            CodeAssetLifecycle.VALIDATED.value,
            CodeAssetLifecycle.PROMOTED.value,
            CodeAssetLifecycle.DEPRECATED.value,
        },
        CodeAssetLifecycle.PROMOTED.value: {
            CodeAssetLifecycle.PROMOTED.value,
            CodeAssetLifecycle.DEPRECATED.value,
        },
        CodeAssetLifecycle.DEPRECATED.value: {
            CodeAssetLifecycle.DEPRECATED.value,
        },
    }

    @classmethod
    def can_transition(
        cls,
        current: str,
        target: str,
    ) -> bool:
        return target in cls._ALLOWED.get(
            current,
            set(),
        )

    @classmethod
    def transition(
        cls,
        asset: CodeAsset,
        target: str,
    ) -> CodeAsset:
        target = str(target)

        if not cls.can_transition(
            asset.lifecycle,
            target,
        ):
            raise ValueError(
                f"Invalid Code Library lifecycle transition: "
                f"{asset.lifecycle} -> {target}"
            )

        asset.lifecycle = target
        return asset

    @classmethod
    def validate(cls, asset: CodeAsset) -> CodeAsset:
        return cls.transition(
            asset,
            CodeAssetLifecycle.VALIDATED.value,
        )

    @classmethod
    def promote(cls, asset: CodeAsset) -> CodeAsset:
        return cls.transition(
            asset,
            CodeAssetLifecycle.PROMOTED.value,
        )

    @classmethod
    def deprecate(cls, asset: CodeAsset) -> CodeAsset:
        return cls.transition(
            asset,
            CodeAssetLifecycle.DEPRECATED.value,
        )


lifecycle = CodeLibraryLifecycle()

__all__ = (
    "CodeLibraryLifecycle",
    "lifecycle",
)
