from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AndroidCompatibilityContext:
    android_api: int = 0
    min_api: int = 0
    target_api: int = 0
    python_version: str = ""
    chaquopy_version: str = ""
    architecture: str = ""
    supported_abis: tuple[str, ...] = ()
    offline: bool = True

    def __post_init__(self) -> None:
        if self.android_api < 0:
            raise ValueError("android_api must not be negative")

        if self.min_api < 0:
            raise ValueError("min_api must not be negative")

        if self.target_api < 0:
            raise ValueError("target_api must not be negative")

        if (
            self.min_api
            and self.target_api
            and self.target_api < self.min_api
        ):
            raise ValueError(
                "target_api must be greater than or equal to min_api"
            )

        normalized_abis = tuple(
            sorted(
                dict.fromkeys(
                    abi.strip().lower()
                    for abi in self.supported_abis
                    if isinstance(abi, str)
                    and abi.strip()
                )
            )
        )

        object.__setattr__(
            self,
            "supported_abis",
            normalized_abis,
        )

    def to_dict(self) -> dict:
        return {
            "android_api": self.android_api,
            "min_api": self.min_api,
            "target_api": self.target_api,
            "python_version": self.python_version,
            "chaquopy_version": self.chaquopy_version,
            "architecture": self.architecture,
            "supported_abis": list(self.supported_abis),
            "offline": self.offline,
        }


@dataclass(frozen=True)
class AndroidCompatibilityResult:
    compatible: bool
    score: float
    reasons: tuple[str, ...]
    unsupported_features: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "unsupported_features": list(
                self.unsupported_features
            ),
            "missing_requirements": list(
                self.missing_requirements
            ),
            "metadata": dict(self.metadata),
        }


class CodeLibraryAndroidCompatibilityEngine:
    """
    Validates Code Library assets against Android and Chaquopy
    execution constraints without requiring Android tooling at
    analysis time.
    """

    DEFAULT_SUPPORTED_PYTHON = (
        "3.8",
        "3.9",
        "3.10",
        "3.11",
        "3.12",
        "3.13",
    )

    DEFAULT_ABIS = (
        "arm64-v8a",
        "armeabi-v7a",
        "x86",
        "x86_64",
    )

    def __init__(
        self,
        *,
        supported_python_versions: Iterable[str] = DEFAULT_SUPPORTED_PYTHON,
        supported_abis: Iterable[str] = DEFAULT_ABIS,
        minimum_android_api: int = 21,
    ) -> None:
        if minimum_android_api < 0:
            raise ValueError(
                "minimum_android_api must not be negative"
            )

        self.supported_python_versions = tuple(
            sorted(
                dict.fromkeys(
                    value.strip()
                    for value in supported_python_versions
                    if isinstance(value, str)
                    and value.strip()
                )
            )
        )

        self.supported_abis = tuple(
            sorted(
                dict.fromkeys(
                    value.strip().lower()
                    for value in supported_abis
                    if isinstance(value, str)
                    and value.strip()
                )
            )
        )

        self.minimum_android_api = minimum_android_api

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        return value.strip().lower()

    @staticmethod
    def _version_matches(
        requested: str,
        supported: tuple[str, ...],
    ) -> bool:
        if not requested:
            return True

        return requested.strip() in supported

    def analyze(
        self,
        asset,
        context: AndroidCompatibilityContext,
    ) -> AndroidCompatibilityResult:
        if not isinstance(
            context,
            AndroidCompatibilityContext,
        ):
            raise TypeError(
                "context must be AndroidCompatibilityContext"
            )

        reasons: list[str] = []
        unsupported: list[str] = []
        missing: list[str] = []

        asset_platforms = tuple(
            getattr(asset, "platforms", ())
        )

        asset_runtime = self._normalize(
            getattr(asset, "runtime", "")
        )

        asset_language = self._normalize(
            getattr(asset, "language", "")
        )

        asset_metadata = getattr(
            asset,
            "metadata",
            {},
        )

        if asset_platforms:
            normalized_platforms = {
                self._normalize(value)
                for value in asset_platforms
                if isinstance(value, str)
            }

            if (
                "android" not in normalized_platforms
                and "mobile" not in normalized_platforms
            ):
                unsupported.append(
                    "android_platform_not_declared"
                )
            else:
                reasons.append(
                    "android_platform_supported"
                )
        else:
            reasons.append(
                "platform_information_not_declared"
            )

        if asset_language:
            if asset_language == "python":
                reasons.append(
                    "python_language_supported"
                )
            else:
                unsupported.append(
                    "language_not_chaquopy_compatible"
                )

        if asset_runtime:
            if asset_runtime in {
                "python",
                "python3",
                "chaquopy",
            }:
                reasons.append(
                    "python_runtime_supported"
                )
            else:
                unsupported.append(
                    "runtime_not_chaquopy_compatible"
                )

        requested_python = (
            context.python_version.strip()
        )

        if requested_python:
            if self._version_matches(
                requested_python,
                self.supported_python_versions,
            ):
                reasons.append(
                    "python_version_supported"
                )
            else:
                unsupported.append(
                    "python_version_unsupported"
                )

        if context.android_api:
            if (
                context.android_api
                < self.minimum_android_api
            ):
                unsupported.append(
                    "android_api_below_minimum"
                )
            else:
                reasons.append(
                    "android_api_supported"
                )

        if context.min_api:
            if (
                context.min_api
                < self.minimum_android_api
            ):
                unsupported.append(
                    "minimum_android_api_unsupported"
                )
            else:
                reasons.append(
                    "minimum_android_api_supported"
                )

        if context.target_api:
            if (
                context.target_api
                < self.minimum_android_api
            ):
                unsupported.append(
                    "target_android_api_unsupported"
                )
            else:
                reasons.append(
                    "target_android_api_supported"
                )

        if context.architecture:
            architecture = self._normalize(
                context.architecture
            )

            if architecture in self.supported_abis:
                reasons.append(
                    "architecture_supported"
                )
            elif architecture in {
                "arm64",
                "arm64-v8a",
                "aarch64",
            }:
                if "arm64-v8a" in self.supported_abis:
                    reasons.append(
                        "architecture_supported"
                    )
                else:
                    unsupported.append(
                        "architecture_unsupported"
                    )
            else:
                unsupported.append(
                    "architecture_unsupported"
                )

        for abi in context.supported_abis:
            if abi not in self.supported_abis:
                unsupported.append(
                    f"unsupported_abi:{abi}"
                )

        chaquopy_declared = bool(
            context.chaquopy_version
            or asset_metadata.get(
                "chaquopy_version"
            )
        )

        if chaquopy_declared:
            reasons.append(
                "chaquopy_configuration_present"
            )
        else:
            missing.append(
                "chaquopy_version"
            )

        if context.offline:
            offline_ready = asset_metadata.get(
                "offline_ready",
                True,
            )

            if offline_ready:
                reasons.append(
                    "offline_execution_supported"
                )
            else:
                unsupported.append(
                    "offline_execution_unsupported"
                )

        if not asset:
            missing.append(
                "asset"
            )

        unsupported = tuple(
            dict.fromkeys(unsupported)
        )

        missing = tuple(
            dict.fromkeys(missing)
        )

        reasons = tuple(
            dict.fromkeys(reasons)
        )

        compatible = not unsupported and not missing

        if compatible:
            score = 10.0
        else:
            deductions = (
                len(unsupported) * 2.5
                + len(missing) * 1.5
            )
            score = max(
                0.0,
                10.0 - deductions,
            )

        return AndroidCompatibilityResult(
            compatible=compatible,
            score=score,
            reasons=reasons,
            unsupported_features=unsupported,
            missing_requirements=missing,
            metadata={
                "asset_id": getattr(
                    asset,
                    "asset_id",
                    "",
                ),
                "asset_name": getattr(
                    asset,
                    "name",
                    "",
                ),
                "python_version": (
                    context.python_version
                ),
                "chaquopy_version": (
                    context.chaquopy_version
                ),
                "android_api": (
                    context.android_api
                ),
                "architecture": (
                    context.architecture
                ),
                "offline": context.offline,
            },
        )

    def is_compatible(
        self,
        asset,
        context: AndroidCompatibilityContext,
    ) -> bool:
        return self.analyze(
            asset,
            context,
        ).compatible

    def score(
        self,
        asset,
        context: AndroidCompatibilityContext,
    ) -> float:
        return self.analyze(
            asset,
            context,
        ).score


__all__ = [
    "AndroidCompatibilityContext",
    "AndroidCompatibilityResult",
    "CodeLibraryAndroidCompatibilityEngine",
]
