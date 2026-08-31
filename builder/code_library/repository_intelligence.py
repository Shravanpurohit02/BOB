from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .construction_plan import (
    ConstructionPlanResult,
)


@dataclass(frozen=True)
class RepositoryFile:
    path: str
    extension: str
    size: int
    is_directory: bool = False

    def __post_init__(self) -> None:
        if not self.path.strip():
            raise ValueError("path must not be empty")

        if self.size < 0:
            raise ValueError("size must be >= 0")

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "extension": self.extension,
            "size": self.size,
            "is_directory": self.is_directory,
        }


@dataclass(frozen=True)
class RepositoryIntelligenceResult:
    repository_root: str
    files: tuple[RepositoryFile, ...]
    existing_assets: tuple[str, ...]
    planned_assets: tuple[str, ...]
    integration_points: tuple[str, ...]
    missing_assets: tuple[str, ...]
    conflicts: tuple[str, ...]
    analyzed: bool
    compatible: bool
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "repository_root": self.repository_root,
            "files": [
                file.to_dict()
                for file in self.files
            ],
            "existing_assets": list(
                self.existing_assets
            ),
            "planned_assets": list(
                self.planned_assets
            ),
            "integration_points": list(
                self.integration_points
            ),
            "missing_assets": list(
                self.missing_assets
            ),
            "conflicts": list(
                self.conflicts
            ),
            "analyzed": self.analyzed,
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryRepositoryIntelligence:
    """
    Inspects an existing repository and compares its current structure
    with a validated CL-15.5 construction plan.

    The analysis is deterministic and read-only.
    """

    def analyze(
        self,
        repository_root: str | Path,
        plan: ConstructionPlanResult,
    ) -> RepositoryIntelligenceResult:
        if not isinstance(
            plan,
            ConstructionPlanResult,
        ):
            raise TypeError(
                "plan must be ConstructionPlanResult"
            )

        root = Path(repository_root).expanduser()

        if not root.exists():
            raise FileNotFoundError(
                f"repository root does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"repository root is not a directory: {root}"
            )

        files: list[RepositoryFile] = []

        for item in sorted(
            root.rglob("*"),
            key=lambda value: str(value.relative_to(root)),
        ):
            relative = str(
                item.relative_to(root)
            )

            if item.is_dir():
                files.append(
                    RepositoryFile(
                        path=relative,
                        extension="",
                        size=0,
                        is_directory=True,
                    )
                )
                continue

            suffix = item.suffix.lower()

            try:
                size = item.stat().st_size
            except OSError:
                size = 0

            files.append(
                RepositoryFile(
                    path=relative,
                    extension=suffix,
                    size=size,
                    is_directory=False,
                )
            )

        existing_names = {
            Path(file.path).stem
            for file in files
            if not file.is_directory
        }

        planned_assets = tuple(
            step.asset_id
            for step in plan.steps
        )

        existing_assets = tuple(
            asset_id
            for asset_id in planned_assets
            if asset_id in existing_names
            or self._asset_path_exists(
                root,
                asset_id,
            )
        )

        missing_assets = tuple(
            asset_id
            for asset_id in planned_assets
            if asset_id not in existing_assets
        )

        integration_points = tuple(
            sorted(
                file.path
                for file in files
                if (
                    not file.is_directory
                    and file.extension
                    in {
                        ".py",
                        ".json",
                        ".toml",
                        ".yaml",
                        ".yml",
                    }
                )
            )
        )

        conflicts = tuple(
            sorted(
                self._detect_conflicts(
                    files,
                    planned_assets,
                )
            )
        )

        compatible = (
            plan.executable
            and not conflicts
        )

        reasons = [
            "repository_scanned",
        ]

        if files:
            reasons.append(
                "repository_structure_detected"
            )

        if existing_assets:
            reasons.append(
                "existing_assets_detected"
            )

        if missing_assets:
            reasons.append(
                "planned_assets_missing"
            )
        else:
            reasons.append(
                "planned_assets_available"
            )

        if integration_points:
            reasons.append(
                "integration_points_detected"
            )

        if conflicts:
            reasons.append(
                "repository_conflicts_detected"
            )
        else:
            reasons.append(
                "no_repository_conflicts"
            )

        if compatible:
            reasons.append(
                "repository_compatible"
            )
        else:
            reasons.append(
                "repository_requires_adaptation"
            )

        if compatible:
            score = 10.0
        else:
            score = max(
                0.0,
                10.0
                - len(conflicts) * 3.0
                - len(missing_assets) * 1.0,
            )

        return RepositoryIntelligenceResult(
            repository_root=str(root),
            files=tuple(files),
            existing_assets=existing_assets,
            planned_assets=planned_assets,
            integration_points=integration_points,
            missing_assets=missing_assets,
            conflicts=conflicts,
            analyzed=True,
            compatible=compatible,
            score=score,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "file_count": len(files),
                "planned_asset_count": len(
                    planned_assets
                ),
                "existing_asset_count": len(
                    existing_assets
                ),
                "missing_asset_count": len(
                    missing_assets
                ),
                "integration_point_count": len(
                    integration_points
                ),
                "conflict_count": len(
                    conflicts
                ),
            },
        )

    @staticmethod
    def _asset_path_exists(
        root: Path,
        asset_id: str,
    ) -> bool:
        for candidate in (
            root / asset_id,
            root / f"{asset_id}.py",
            root / "builder" / f"{asset_id}.py",
            root / "src" / f"{asset_id}.py",
        ):
            if candidate.exists():
                return True

        return False

    @staticmethod
    def _detect_conflicts(
        files: tuple[RepositoryFile, ...] | list[RepositoryFile],
        planned_assets: tuple[str, ...],
    ) -> list[str]:
        conflicts: list[str] = []

        for asset_id in planned_assets:
            matches = [
                file.path
                for file in files
                if (
                    not file.is_directory
                    and Path(file.path).stem
                    == asset_id
                )
            ]

            if len(matches) > 1:
                conflicts.append(
                    f"{asset_id}:multiple_existing_files"
                )

        return conflicts

    def analyze_plan(
        self,
        repository_root: str | Path,
        plan: ConstructionPlanResult,
    ) -> RepositoryIntelligenceResult:
        return self.analyze(
            repository_root,
            plan,
        )


__all__ = [
    "RepositoryFile",
    "RepositoryIntelligenceResult",
    "CodeLibraryRepositoryIntelligence",
]
