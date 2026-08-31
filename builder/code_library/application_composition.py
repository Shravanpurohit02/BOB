from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Iterable

from builder.codegen.artifacts import (
    GeneratedArtifact,
    GeneratedDirectory,
    GeneratedFile,
)

from .models import CodeAsset, CodeAssetLifecycle
from .provenance import CodeLibraryProvenance
from .retrieval import CodeLibraryRetrievalEngine


class ApplicationCompositionError(ValueError):
    """Raised when Code Library assets cannot form a valid application."""


@dataclass(slots=True, frozen=True)
class ApplicationCompositionRequest:
    query: str
    limit: int = 20
    asset_type: str | None = None
    language: str | None = None
    framework: str | None = None
    runtime: str | None = None
    tag: str | None = None
    capability: str | None = None
    dependency: str | None = None
    parent_id: str | None = None
    include_draft: bool = False
    include_deprecated: bool = False


@dataclass(slots=True, frozen=True)
class ApplicationCompositionMapping:
    asset_id: str
    asset_name: str
    source_path: str
    output_path: str
    action: str
    content_length: int


@dataclass(slots=True)
class ApplicationCompositionResult:
    success: bool = False
    query: str = ""
    assets: list[CodeAsset] = field(default_factory=list)
    artifacts: list[GeneratedArtifact] = field(default_factory=list)
    mappings: list[ApplicationCompositionMapping] = field(
        default_factory=list
    )
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def generated_files(self) -> list[str]:
        return [
            generated.path
            for artifact in self.artifacts
            for generated in artifact.files
        ]

    @property
    def directories(self) -> list[str]:
        return [
            directory.path
            for artifact in self.artifacts
            for directory in artifact.directories
        ]


class ApplicationCompositionEngine:
    """
    Deterministic application assembly boundary for the BOB Code Library.

    CL-1 through CL-5 remain authoritative for asset identity, persistence,
    lifecycle, provenance, retrieval and single-asset composition.

    CL-6 assembles multiple canonical assets into the existing
    GeneratedArtifact representation.

    This engine never writes to the filesystem and never executes operations.
    """

    def __init__(
        self,
        retrieval: CodeLibraryRetrievalEngine | None = None,
    ) -> None:
        self.retrieval = retrieval or CodeLibraryRetrievalEngine()

    @staticmethod
    def _asset_files(asset: CodeAsset) -> Iterable:
        for item in asset.files:
            yield item

    @staticmethod
    def _normal_path(path: str) -> str:
        value = str(path or "").strip().replace("\\", "/")

        if not value:
            raise ApplicationCompositionError(
                "Code Library asset contains an empty file path."
            )

        candidate = PurePosixPath(value)

        if candidate.is_absolute():
            raise ApplicationCompositionError(
                f"Code Library asset contains an absolute path: {value}"
            )

        if ".." in candidate.parts:
            raise ApplicationCompositionError(
                f"Code Library asset escapes the application root: {value}"
            )

        return candidate.as_posix()

    @staticmethod
    def _asset_sort_key(asset: CodeAsset) -> tuple:
        return (
            str(asset.parent_id or ""),
            str(asset.asset_type or "").lower(),
            str(asset.name or "").lower(),
            str(asset.id),
        )

    @staticmethod
    def _validate_asset(asset: CodeAsset) -> None:
        if not str(asset.id).strip():
            raise ApplicationCompositionError(
                "Cannot compose an asset without an id."
            )

        if not str(asset.name).strip():
            raise ApplicationCompositionError(
                f"Code Library asset has no name: {asset.id}"
            )

        if asset.lifecycle not in {
            CodeAssetLifecycle.VALIDATED.value,
            CodeAssetLifecycle.PROMOTED.value,
        }:
            raise ApplicationCompositionError(
                f"Asset is not composition-eligible: {asset.id}"
            )

        valid, reason = CodeLibraryProvenance.validate_asset(asset)

        if not valid:
            raise ApplicationCompositionError(
                f"Asset provenance is invalid: {asset.id}: {reason}"
            )

    def _retrieve(
        self,
        request: ApplicationCompositionRequest,
    ) -> list[CodeAsset]:
        result = self.retrieval.search(
            request.query,
            asset_type=request.asset_type,
            language=request.language,
            framework=request.framework,
            runtime=request.runtime,
            tag=request.tag,
            capability=request.capability,
            dependency=request.dependency,
            parent_id=request.parent_id,
            limit=max(0, int(request.limit)),
            include_draft=request.include_draft,
            include_deprecated=request.include_deprecated,
        )

        assets = [
            item.asset
            for item in result.records
        ]

        if not assets:
            raise ApplicationCompositionError(
                f"No Code Library assets matched composition query: "
                f"{request.query!r}"
            )

        return sorted(
            assets,
            key=self._asset_sort_key,
        )

    def compose(
        self,
        request: ApplicationCompositionRequest,
    ) -> ApplicationCompositionResult:
        result = ApplicationCompositionResult(
            query=request.query,
        )

        try:
            assets = self._retrieve(request)

            seen_assets: set[str] = set()
            seen_files: dict[str, str] = {}
            generated = GeneratedArtifact()

            for asset in assets:
                self._validate_asset(asset)

                if asset.id in seen_assets:
                    raise ApplicationCompositionError(
                        f"Duplicate Code Library asset: {asset.id}"
                    )

                seen_assets.add(asset.id)
                result.assets.append(asset)

                for source in self._asset_files(asset):
                    source_path = self._normal_path(
                        getattr(source, "path", "")
                    )

                    output_path = source_path

                    owner = seen_files.get(output_path)

                    if owner is not None:
                        raise ApplicationCompositionError(
                            "Application composition produced a file "
                            f"collision at {output_path!r}: "
                            f"{owner!r} and {asset.id!r}"
                        )

                    seen_files[output_path] = asset.id

                    content = getattr(source, "content", "")

                    if not isinstance(content, str):
                        raise ApplicationCompositionError(
                            f"Asset file content must be text: "
                            f"{asset.id}:{source_path}"
                        )

                    generated.files.append(
                        GeneratedFile(
                            path=output_path,
                            action="create",
                            language=str(
                                getattr(
                                    source,
                                    "language",
                                    None,
                                )
                                or asset.language
                                or "python"
                            ),
                            content=content,
                        )
                    )

                    result.mappings.append(
                        ApplicationCompositionMapping(
                            asset_id=asset.id,
                            asset_name=asset.name,
                            source_path=source_path,
                            output_path=output_path,
                            action="create",
                            content_length=len(content),
                        )
                    )

            directories: set[str] = set()

            for file in generated.files:
                parent = PurePosixPath(file.path).parent

                if str(parent) not in {"", "."}:
                    parts = parent.parts

                    for index in range(1, len(parts) + 1):
                        directories.add(
                            PurePosixPath(
                                *parts[:index]
                            ).as_posix()
                        )

            generated.directories.extend(
                GeneratedDirectory(path=directory)
                for directory in sorted(directories)
            )

            if not generated.files:
                raise ApplicationCompositionError(
                    "Selected Code Library assets contain no files."
                )

            result.artifacts.append(generated)
            result.success = True
            return result

        except ApplicationCompositionError as exc:
            result.errors.append(str(exc))
            return result


application_composition = ApplicationCompositionEngine()


__all__ = (
    "ApplicationCompositionError",
    "ApplicationCompositionMapping",
    "ApplicationCompositionRequest",
    "ApplicationCompositionResult",
    "ApplicationCompositionEngine",
    "application_composition",
)
