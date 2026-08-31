from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
import re

from builder.codegen.artifacts import (
    GeneratedArtifact,
    GeneratedDirectory,
    GeneratedFile,
)

from .models import CodeAsset, CodeAssetLifecycle
from .provenance import CodeLibraryProvenance


class CodeLibraryCompositionError(ValueError):
    """Raised when a Code Library asset cannot be composed safely."""


@dataclass(slots=True, frozen=True)
class CompositionRequest:
    asset: CodeAsset
    variables: dict[str, object] = field(default_factory=dict)
    destination: str = ""


@dataclass(slots=True, frozen=True)
class CompositionResult:
    asset_id: str
    asset_version: str
    asset_fingerprint: str
    artifact: GeneratedArtifact
    files: tuple[str, ...]
    directories: tuple[str, ...]
    substitutions: tuple[str, ...]
    metadata: dict[str, object]


class CodeLibraryCompositionEngine:
    """
    Production composition boundary for canonical Code Library assets.

    Composition never writes to the filesystem. It transforms one
    canonical CodeAsset into the existing GeneratedArtifact contract
    consumed by BOB's engineering/artifact pipeline.

    Template syntax:

        {{variable}}

    Variables are substituted in both asset file paths and file contents.
    Missing variables, unsafe paths, duplicate output paths and invalid
    assets are rejected deterministically.
    """

    _VARIABLE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")

    def compose(
        self,
        asset: CodeAsset,
        variables: dict[str, object] | None = None,
        *,
        destination: str = "",
    ) -> CompositionResult:
        self._validate_asset(asset)

        values = {
            str(key): str(value)
            for key, value in (variables or {}).items()
        }

        destination = self._normalize_destination(destination)

        generated_files: list[GeneratedFile] = []
        directories: set[str] = set()
        substitutions: set[str] = set()
        seen: set[str] = set()

        for source_file in asset.files:
            relative_path = self._substitute(
                source_file.path,
                values,
                substitutions,
            )

            relative_path = self._safe_relative_path(
                relative_path
            )

            output_path = (
                f"{destination}/{relative_path}"
                if destination
                else relative_path
            )

            output_path = self._safe_relative_path(
                output_path
            )

            if output_path in seen:
                raise CodeLibraryCompositionError(
                    f"Duplicate composed output path: {output_path}"
                )

            seen.add(output_path)

            content = self._substitute(
                source_file.content,
                values,
                substitutions,
            )

            generated_files.append(
                GeneratedFile(
                    path=output_path,
                    action="create",
                    language=source_file.language or asset.language or "python",
                    content=content,
                )
            )

            parent = PurePosixPath(output_path).parent.as_posix()

            if parent not in ("", "."):
                parts = PurePosixPath(parent).parts
                current = ""

                for part in parts:
                    current = (
                        part
                        if not current
                        else f"{current}/{part}"
                    )
                    directories.add(current)

        generated_directories = [
            GeneratedDirectory(path=path)
            for path in sorted(directories)
        ]

        artifact = GeneratedArtifact(
            files=generated_files,
            directories=generated_directories,
        )

        return CompositionResult(
            asset_id=asset.id,
            asset_version=asset.version,
            asset_fingerprint=asset.fingerprint,
            artifact=artifact,
            files=tuple(file.path for file in generated_files),
            directories=tuple(sorted(directories)),
            substitutions=tuple(sorted(substitutions)),
            metadata={
                "composition": "code_library",
                "asset_id": asset.id,
                "asset_version": asset.version,
                "asset_fingerprint": asset.fingerprint,
                "asset_stable_id": asset.stable_id,
                "asset_type": asset.asset_type,
                "asset_lifecycle": asset.lifecycle,
                "source": asset.provenance.source,
                "source_type": asset.provenance.source_type,
                "license": asset.provenance.license,
                "destination": destination,
                "file_count": len(generated_files),
                "directory_count": len(generated_directories),
                "substitution_count": len(substitutions),
            },
        )

    @staticmethod
    def _validate_asset(asset: CodeAsset) -> None:
        if not isinstance(asset, CodeAsset):
            raise CodeLibraryCompositionError(
                "Composition requires a canonical CodeAsset."
            )

        if not asset.id.strip():
            raise CodeLibraryCompositionError(
                "Code Library asset id is required."
            )

        if not asset.name.strip():
            raise CodeLibraryCompositionError(
                "Code Library asset name is required."
            )

        if not asset.files:
            raise CodeLibraryCompositionError(
                f"Code Library asset contains no files: {asset.id}"
            )

        if asset.lifecycle == CodeAssetLifecycle.DRAFT.value:
            raise CodeLibraryCompositionError(
                f"Draft Code Library assets cannot be composed: {asset.id}"
            )

        if asset.lifecycle == CodeAssetLifecycle.DEPRECATED.value:
            raise CodeLibraryCompositionError(
                f"Deprecated Code Library assets cannot be composed: {asset.id}"
            )

        if asset.lifecycle not in {
            CodeAssetLifecycle.VALIDATED.value,
            CodeAssetLifecycle.PROMOTED.value,
        }:
            raise CodeLibraryCompositionError(
                f"Unsupported Code Library lifecycle: {asset.lifecycle}"
            )

        valid, issues = CodeLibraryProvenance.validate_asset(asset)

        if not valid:
            raise CodeLibraryCompositionError(
                "Code Library asset has invalid provenance: "
                + "; ".join(issues)
            )

    @classmethod
    def _substitute(
        cls,
        value: str,
        variables: dict[str, str],
        substitutions: set[str],
    ) -> str:
        value = str(value)

        missing: set[str] = set()

        def replace(match: re.Match[str]) -> str:
            name = match.group(1)

            if name not in variables:
                missing.add(name)
                return match.group(0)

            substitutions.add(name)
            return variables[name]

        result = cls._VARIABLE.sub(
            replace,
            value,
        )

        if missing:
            raise CodeLibraryCompositionError(
                "Missing composition variables: "
                + ", ".join(sorted(missing))
            )

        return result

    @staticmethod
    def _normalize_destination(value: str) -> str:
        value = str(value or "").strip().replace("\\", "/")

        if not value:
            return ""

        return CodeLibraryCompositionEngine._safe_relative_path(
            value
        )

    @staticmethod
    def _safe_relative_path(value: str) -> str:
        value = str(value or "").strip().replace("\\", "/")

        if not value:
            raise CodeLibraryCompositionError(
                "Composed artifact path cannot be empty."
            )

        path = PurePosixPath(value)

        if path.is_absolute():
            raise CodeLibraryCompositionError(
                f"Absolute composed artifact path is forbidden: {value}"
            )

        parts = path.parts

        if any(
            part in ("", ".", "..")
            for part in parts
        ):
            raise CodeLibraryCompositionError(
                f"Unsafe composed artifact path: {value}"
            )

        return path.as_posix()


composition = CodeLibraryCompositionEngine()

__all__ = (
    "CodeLibraryCompositionEngine",
    "CodeLibraryCompositionError",
    "CompositionRequest",
    "CompositionResult",
    "composition",
)
