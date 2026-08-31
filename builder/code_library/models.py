from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(*values: str) -> str:
    payload = "\n".join(str(value) for value in values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CodeAssetType(str, Enum):
    APPLICATION = "application"
    SYSTEM = "system"
    PAGE = "page"
    COMPONENT = "component"
    PATTERN = "pattern"
    WORKFLOW = "workflow"
    DATA_MODEL = "data_model"


class CodeAssetLifecycle(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    PROMOTED = "promoted"
    DEPRECATED = "deprecated"


@dataclass(slots=True)
class CodeAssetFile:
    path: str
    content: str = ""
    language: str = ""
    executable: bool = False

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            self.content.encode("utf-8")
        ).hexdigest()


@dataclass(slots=True)
class CodeAssetProvenance:
    source: str = ""
    source_type: str = ""
    author: str = ""
    license: str = ""
    license_url: str = ""
    attribution: str = ""
    reference: str = ""
    imported_at: str = field(default_factory=_now)
    notes: str = ""


@dataclass(slots=True)
class CodeAssetRelationship:
    source_id: str
    target_id: str
    relation: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CodeAssetVersion:
    version: str
    fingerprint: str
    created_at: str = field(default_factory=_now)
    changelog: str = ""
    source_reference: str = ""


@dataclass(slots=True)
class CodeAssetUsage:
    uses: int = 0
    successes: int = 0
    failures: int = 0
    last_used_at: str = ""
    last_success_at: str = ""
    last_failure_at: str = ""

    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        if total == 0:
            return 0.0
        return self.successes / total


@dataclass(slots=True)
class CodeAsset:
    id: str
    asset_type: str
    name: str
    description: str = ""

    language: str = ""
    framework: str = ""
    runtime: str = ""
    version: str = "1.0.0"

    tags: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)

    parent_id: str = ""

    files: list[CodeAssetFile] = field(default_factory=list)
    relationships: list[CodeAssetRelationship] = field(
        default_factory=list
    )

    provenance: CodeAssetProvenance = field(
        default_factory=CodeAssetProvenance
    )

    versions: list[CodeAssetVersion] = field(
        default_factory=list
    )

    usage: CodeAssetUsage = field(
        default_factory=CodeAssetUsage
    )

    lifecycle: str = CodeAssetLifecycle.DRAFT.value

    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        parts = [
            self.asset_type,
            self.name,
            self.language,
            self.framework,
            self.runtime,
            self.version,
        ]

        for item in sorted(
            self.files,
            key=lambda value: value.path,
        ):
            parts.extend(
                (
                    item.path,
                    item.fingerprint,
                )
            )

        return _stable_id(*parts)

    @property
    def stable_id(self) -> str:
        return _stable_id(
            self.asset_type,
            self.name,
            self.fingerprint,
        )

    @property
    def success_rate(self) -> float:
        return self.usage.success_rate

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
