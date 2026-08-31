from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class AndroidPackagingContext:
    package_name: str
    version_name: str = "1.0.0"
    version_code: int = 1
    min_sdk: int = 24
    target_sdk: int = 35
    compile_sdk: int = 35
    python_version: str = ""
    chaquopy_version: str = ""
    architectures: tuple[str, ...] = (
        "arm64-v8a",
        "armeabi-v7a",
    )
    offline: bool = True

    def __post_init__(self) -> None:
        if not self.package_name.strip():
            raise ValueError("package_name must not be empty")
        if self.version_code < 1:
            raise ValueError("version_code must be positive")
        if self.min_sdk < 1:
            raise ValueError("min_sdk must be positive")
        if self.target_sdk < self.min_sdk:
            raise ValueError(
                "target_sdk must be greater than or equal to min_sdk"
            )
        if self.compile_sdk < self.target_sdk:
            raise ValueError(
                "compile_sdk must be greater than or equal to target_sdk"
            )

    def to_dict(self) -> dict:
        return {
            "package_name": self.package_name,
            "version_name": self.version_name,
            "version_code": self.version_code,
            "min_sdk": self.min_sdk,
            "target_sdk": self.target_sdk,
            "compile_sdk": self.compile_sdk,
            "python_version": self.python_version,
            "chaquopy_version": self.chaquopy_version,
            "architectures": list(self.architectures),
            "offline": self.offline,
        }


@dataclass(frozen=True)
class AndroidPackageArtifact:
    path: str
    artifact_type: str
    package_name: str
    version_name: str
    version_code: int
    size_bytes: int = 0
    sha256: str = ""
    verified: bool = False
    metadata: dict | None = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "artifact_type": self.artifact_type,
            "package_name": self.package_name,
            "version_name": self.version_name,
            "version_code": self.version_code,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "verified": self.verified,
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class AndroidPackagingPlan:
    package_name: str
    version_name: str
    version_code: int
    min_sdk: int
    target_sdk: int
    compile_sdk: int
    architectures: tuple[str, ...]
    offline: bool
    required_files: tuple[str, ...]
    required_directories: tuple[str, ...]
    artifact_types: tuple[str, ...]
    compatible: bool
    ready: bool
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "package_name": self.package_name,
            "version_name": self.version_name,
            "version_code": self.version_code,
            "min_sdk": self.min_sdk,
            "target_sdk": self.target_sdk,
            "compile_sdk": self.compile_sdk,
            "architectures": list(self.architectures),
            "offline": self.offline,
            "required_files": list(self.required_files),
            "required_directories": list(self.required_directories),
            "artifact_types": list(self.artifact_types),
            "compatible": self.compatible,
            "ready": self.ready,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryAndroidPackagingEngine:
    """
    Produces deterministic Android packaging plans for the offline
    Code Library.

    This subsystem plans packaging requirements; it does not invoke
    Gradle, Android Studio, or external network services.
    """

    REQUIRED_FILES = (
        "settings.gradle",
        "build.gradle",
        "gradle.properties",
        "app/build.gradle",
        "app/src/main/AndroidManifest.xml",
    )

    REQUIRED_DIRECTORIES = (
        "app",
        "app/src/main",
        "app/src/main/java",
        "app/src/main/res",
        "app/src/main/python",
    )

    DEFAULT_ARTIFACT_TYPES = (
        "apk",
        "aab",
    )

    def create_plan(
        self,
        context: AndroidPackagingContext,
        *,
        artifact_types: Iterable[str] = DEFAULT_ARTIFACT_TYPES,
    ) -> AndroidPackagingPlan:
        normalized_artifacts = tuple(
            dict.fromkeys(
                artifact.strip().lower()
                for artifact in artifact_types
                if artifact and artifact.strip()
            )
        )

        if not normalized_artifacts:
            raise ValueError(
                "artifact_types must contain at least one artifact"
            )

        supported = {"apk", "aab"}

        unsupported = tuple(
            artifact
            for artifact in normalized_artifacts
            if artifact not in supported
        )

        reasons: list[str] = []

        compatible = not unsupported

        if unsupported:
            reasons.append("unsupported_artifact_type")

        if context.offline:
            reasons.append("offline_packaging_enabled")
        else:
            reasons.append("online_packaging_enabled")

        if context.python_version:
            reasons.append("python_runtime_declared")

        if context.chaquopy_version:
            reasons.append("chaquopy_version_declared")

        if context.architectures:
            reasons.append("android_architectures_declared")
        else:
            compatible = False
            reasons.append("android_architectures_missing")

        if compatible:
            reasons.append("android_packaging_compatible")

        ready = compatible and bool(
            context.package_name.strip()
        )

        if ready:
            reasons.append("android_packaging_ready")
        else:
            reasons.append("android_packaging_blocked")

        score = 10.0 if ready else 0.0

        if compatible and not context.python_version:
            score = max(0.0, score - 1.0)

        if compatible and not context.chaquopy_version:
            score = max(0.0, score - 1.0)

        return AndroidPackagingPlan(
            package_name=context.package_name,
            version_name=context.version_name,
            version_code=context.version_code,
            min_sdk=context.min_sdk,
            target_sdk=context.target_sdk,
            compile_sdk=context.compile_sdk,
            architectures=tuple(context.architectures),
            offline=context.offline,
            required_files=self.REQUIRED_FILES,
            required_directories=self.REQUIRED_DIRECTORIES,
            artifact_types=normalized_artifacts,
            compatible=compatible,
            ready=ready,
            score=score,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "unsupported_artifact_types": list(
                    unsupported
                ),
                "required_file_count": len(
                    self.REQUIRED_FILES
                ),
                "required_directory_count": len(
                    self.REQUIRED_DIRECTORIES
                ),
                "artifact_type_count": len(
                    normalized_artifacts
                ),
            },
        )

    def validate_project_layout(
        self,
        project_root: str | Path,
        context: AndroidPackagingContext,
    ) -> AndroidPackagingPlan:
        root = Path(project_root)

        plan = self.create_plan(context)

        missing_files = tuple(
            relative
            for relative in plan.required_files
            if not (root / relative).is_file()
        )

        missing_directories = tuple(
            relative
            for relative in plan.required_directories
            if not (root / relative).is_dir()
        )

        reasons = list(plan.reasons)

        if missing_files:
            reasons.append("required_files_missing")

        if missing_directories:
            reasons.append("required_directories_missing")

        ready = (
            plan.ready
            and not missing_files
            and not missing_directories
        )

        if ready:
            reasons.append("project_layout_ready")
        else:
            reasons.append("project_layout_incomplete")

        score = plan.score

        if missing_files or missing_directories:
            score = 0.0

        metadata = dict(plan.metadata)
        metadata.update(
            {
                "missing_files": list(missing_files),
                "missing_directories": list(
                    missing_directories
                ),
            }
        )

        return AndroidPackagingPlan(
            package_name=plan.package_name,
            version_name=plan.version_name,
            version_code=plan.version_code,
            min_sdk=plan.min_sdk,
            target_sdk=plan.target_sdk,
            compile_sdk=plan.compile_sdk,
            architectures=plan.architectures,
            offline=plan.offline,
            required_files=plan.required_files,
            required_directories=plan.required_directories,
            artifact_types=plan.artifact_types,
            compatible=plan.compatible,
            ready=ready,
            score=score,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata=metadata,
        )

    @staticmethod
    def artifact_from_path(
        path: str | Path,
        context: AndroidPackagingContext,
        *,
        artifact_type: str | None = None,
        sha256: str = "",
        verified: bool = False,
    ) -> AndroidPackageArtifact:
        artifact_path = Path(path)

        detected_type = (
            artifact_type
            or artifact_path.suffix.lstrip(".").lower()
        )

        if detected_type not in {"apk", "aab"}:
            raise ValueError(
                f"Unsupported Android artifact type: {detected_type}"
            )

        size = (
            artifact_path.stat().st_size
            if artifact_path.is_file()
            else 0
        )

        return AndroidPackageArtifact(
            path=str(artifact_path),
            artifact_type=detected_type,
            package_name=context.package_name,
            version_name=context.version_name,
            version_code=context.version_code,
            size_bytes=size,
            sha256=sha256,
            verified=verified,
            metadata={
                "exists": artifact_path.is_file(),
                "offline": context.offline,
            },
        )


__all__ = [
    "AndroidPackagingContext",
    "AndroidPackageArtifact",
    "AndroidPackagingPlan",
    "CodeLibraryAndroidPackagingEngine",
]
