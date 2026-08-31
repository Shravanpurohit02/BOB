from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class CompiledPayloadManifest:
    payload_id: str
    version: str
    runtime: str
    python_version: str
    architecture: str
    files: tuple[str, ...]
    checksums: tuple[tuple[str, str], ...]
    metadata: dict

    def __post_init__(self) -> None:
        if not self.payload_id.strip():
            raise ValueError("payload_id must not be empty")

        if not self.version.strip():
            raise ValueError("version must not be empty")

        object.__setattr__(
            self,
            "files",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip()
                        for value in self.files
                        if isinstance(value, str)
                        and value.strip()
                    )
                )
            ),
        )

        normalized_checksums = tuple(
            sorted(
                dict.fromkeys(
                    (
                        str(path).strip(),
                        str(checksum).strip().lower(),
                    )
                    for path, checksum in self.checksums
                    if str(path).strip()
                    and str(checksum).strip()
                )
            )
        )

        object.__setattr__(
            self,
            "checksums",
            normalized_checksums,
        )

    def to_dict(self) -> dict:
        return {
            "payload_id": self.payload_id,
            "version": self.version,
            "runtime": self.runtime,
            "python_version": self.python_version,
            "architecture": self.architecture,
            "files": list(self.files),
            "checksums": {
                path: checksum
                for path, checksum in self.checksums
            },
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class CompiledPayloadVerificationResult:
    valid: bool
    score: float
    reasons: tuple[str, ...]
    missing_files: tuple[str, ...]
    unexpected_files: tuple[str, ...]
    corrupted_files: tuple[str, ...]
    checksum_mismatches: tuple[str, ...]
    metadata_mismatches: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "score": self.score,
            "reasons": list(self.reasons),
            "missing_files": list(self.missing_files),
            "unexpected_files": list(self.unexpected_files),
            "corrupted_files": list(self.corrupted_files),
            "checksum_mismatches": list(
                self.checksum_mismatches
            ),
            "metadata_mismatches": list(
                self.metadata_mismatches
            ),
            "metadata": dict(self.metadata),
        }


class CodeLibraryCompiledPayloadVerifier:
    """
    Verifies compiled/offline Code Library payloads against a manifest.

    Verification is deterministic and local-only. No external service is
    required to validate payload structure, metadata, or file checksums.
    """

    def __init__(
        self,
        *,
        required_files: Iterable[str] = (
            "manifest.json",
        ),
        allowed_extensions: Iterable[str] = (
            ".py",
            ".pyc",
            ".so",
            ".json",
            ".txt",
            ".md",
            ".bin",
        ),
        checksum_algorithm: str = "sha256",
    ) -> None:
        algorithm = checksum_algorithm.strip().lower()

        if algorithm not in hashlib.algorithms_available:
            raise ValueError(
                f"Unsupported checksum algorithm: {algorithm}"
            )

        self.required_files = tuple(
            sorted(
                dict.fromkeys(
                    value.strip()
                    for value in required_files
                    if isinstance(value, str)
                    and value.strip()
                )
            )
        )

        self.allowed_extensions = tuple(
            sorted(
                dict.fromkeys(
                    value.strip().lower()
                    for value in allowed_extensions
                    if isinstance(value, str)
                    and value.strip()
                )
            )
        )

        self.checksum_algorithm = algorithm

    def _checksum(
        self,
        path: Path,
    ) -> str:
        digest = hashlib.new(
            self.checksum_algorithm
        )

        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _relative_files(
        payload_path: Path,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                str(path.relative_to(payload_path))
                for path in payload_path.rglob("*")
                if path.is_file()
            )
        )

    def verify(
        self,
        payload_path: str | Path,
        manifest: CompiledPayloadManifest,
    ) -> CompiledPayloadVerificationResult:
        if not isinstance(
            manifest,
            CompiledPayloadManifest,
        ):
            raise TypeError(
                "manifest must be CompiledPayloadManifest"
            )

        payload = Path(payload_path)

        if not payload.exists():
            return CompiledPayloadVerificationResult(
                valid=False,
                score=0.0,
                reasons=("payload_not_found",),
                missing_files=manifest.files,
                unexpected_files=(),
                corrupted_files=(),
                checksum_mismatches=(),
                metadata_mismatches=(),
                metadata={
                    "payload_path": str(payload),
                    "payload_id": manifest.payload_id,
                },
            )

        if not payload.is_dir():
            return CompiledPayloadVerificationResult(
                valid=False,
                score=0.0,
                reasons=("payload_not_directory",),
                missing_files=(),
                unexpected_files=(),
                corrupted_files=(),
                checksum_mismatches=(),
                metadata_mismatches=(),
                metadata={
                    "payload_path": str(payload),
                    "payload_id": manifest.payload_id,
                },
            )

        actual_files = set(
            self._relative_files(payload)
        )

        expected_files = set(
            manifest.files
        )

        required_files = set(
            self.required_files
        )

        missing = expected_files - actual_files
        missing.update(
            required_files - actual_files
        )

        unexpected = {
            value
            for value in actual_files
            if Path(value).suffix.lower()
            not in self.allowed_extensions
        }

        checksum_mismatches: list[str] = []
        corrupted: list[str] = []

        checksum_map = dict(
            manifest.checksums
        )

        for relative_path, expected_checksum in (
            checksum_map.items()
        ):
            file_path = payload / relative_path

            if not file_path.is_file():
                continue

            actual_checksum = self._checksum(
                file_path
            )

            if actual_checksum != expected_checksum:
                checksum_mismatches.append(
                    relative_path
                )
                corrupted.append(
                    relative_path
                )

        metadata_mismatches: list[str] = []

        manifest_path = payload / "manifest.json"

        if manifest_path.is_file():
            try:
                with manifest_path.open(
                    "r",
                    encoding="utf-8",
                ) as handle:
                    stored_manifest = json.load(handle)

                checks = (
                    ("payload_id", manifest.payload_id),
                    ("version", manifest.version),
                    ("runtime", manifest.runtime),
                    (
                        "python_version",
                        manifest.python_version,
                    ),
                    (
                        "architecture",
                        manifest.architecture,
                    ),
                )

                for key, expected in checks:
                    actual = stored_manifest.get(key)

                    if actual != expected:
                        metadata_mismatches.append(
                            key
                        )

            except (
                OSError,
                ValueError,
                TypeError,
            ):
                metadata_mismatches.append(
                    "manifest.json"
                )
        else:
            missing.add("manifest.json")

        reasons: list[str] = []

        if not missing:
            reasons.append(
                "required_files_present"
            )
        else:
            reasons.append(
                "required_files_missing"
            )

        if not unexpected:
            reasons.append(
                "file_extensions_valid"
            )
        else:
            reasons.append(
                "unsupported_files_present"
            )

        if not checksum_mismatches:
            reasons.append(
                "checksums_verified"
            )
        else:
            reasons.append(
                "checksum_mismatch_detected"
            )

        if not metadata_mismatches:
            reasons.append(
                "manifest_metadata_verified"
            )
        else:
            reasons.append(
                "manifest_metadata_mismatch"
            )

        valid = not (
            missing
            or unexpected
            or corrupted
            or checksum_mismatches
            or metadata_mismatches
        )

        if valid:
            score = 10.0
            reasons.append(
                "compiled_payload_verified"
            )
        else:
            deductions = (
                len(missing) * 2.0
                + len(unexpected) * 1.0
                + len(corrupted) * 3.0
                + len(metadata_mismatches) * 2.0
            )

            score = max(
                0.0,
                10.0 - deductions,
            )

            reasons.append(
                "compiled_payload_verification_failed"
            )

        return CompiledPayloadVerificationResult(
            valid=valid,
            score=score,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            missing_files=tuple(
                sorted(missing)
            ),
            unexpected_files=tuple(
                sorted(unexpected)
            ),
            corrupted_files=tuple(
                sorted(
                    dict.fromkeys(corrupted)
                )
            ),
            checksum_mismatches=tuple(
                sorted(
                    dict.fromkeys(
                        checksum_mismatches
                    )
                )
            ),
            metadata_mismatches=tuple(
                sorted(
                    dict.fromkeys(
                        metadata_mismatches
                    )
                )
            ),
            metadata={
                "payload_path": str(payload),
                "payload_id": manifest.payload_id,
                "version": manifest.version,
                "runtime": manifest.runtime,
                "python_version": manifest.python_version,
                "architecture": manifest.architecture,
                "actual_file_count": len(
                    actual_files
                ),
                "expected_file_count": len(
                    expected_files
                ),
            },
        )

    def verify_manifest_file(
        self,
        payload_path: str | Path,
    ) -> CompiledPayloadVerificationResult:
        payload = Path(payload_path)
        manifest_path = payload / "manifest.json"

        if not manifest_path.is_file():
            return CompiledPayloadVerificationResult(
                valid=False,
                score=0.0,
                reasons=("manifest_missing",),
                missing_files=("manifest.json",),
                unexpected_files=(),
                corrupted_files=(),
                checksum_mismatches=(),
                metadata_mismatches=(),
                metadata={
                    "payload_path": str(payload),
                },
            )

        try:
            with manifest_path.open(
                "r",
                encoding="utf-8",
            ) as handle:
                data = json.load(handle)

            checksums = tuple(
                sorted(
                    (
                        str(path),
                        str(checksum),
                    )
                    for path, checksum
                    in data.get(
                        "checksums",
                        {},
                    ).items()
                )
            )

            manifest = CompiledPayloadManifest(
                payload_id=str(
                    data["payload_id"]
                ),
                version=str(
                    data["version"]
                ),
                runtime=str(
                    data.get("runtime", "")
                ),
                python_version=str(
                    data.get(
                        "python_version",
                        "",
                    )
                ),
                architecture=str(
                    data.get(
                        "architecture",
                        "",
                    )
                ),
                files=tuple(
                    data.get(
                        "files",
                        (),
                    )
                ),
                checksums=checksums,
                metadata=dict(
                    data.get(
                        "metadata",
                        {},
                    )
                ),
            )

        except (
            OSError,
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            return CompiledPayloadVerificationResult(
                valid=False,
                score=0.0,
                reasons=(
                    "manifest_invalid",
                ),
                missing_files=(),
                unexpected_files=(),
                corrupted_files=(),
                checksum_mismatches=(),
                metadata_mismatches=(
                    "manifest.json",
                ),
                metadata={
                    "payload_path": str(payload),
                },
            )

        return self.verify(
            payload,
            manifest,
        )


__all__ = [
    "CompiledPayloadManifest",
    "CompiledPayloadVerificationResult",
    "CodeLibraryCompiledPayloadVerifier",
]
