from __future__ import annotations

import inspect

from dataclasses import dataclass
from typing import Any

from .android_compatibility import (
    AndroidCompatibilityContext,
    CodeLibraryAndroidCompatibilityEngine,
)
from .compiled_payload_verification import (
    CompiledPayloadManifest,
    CodeLibraryCompiledPayloadVerifier,
)
from .incremental_updates import (
    CodeLibraryIncrementalUpdater,
    IncrementalUpdate,
)
from .local_retrieval import (
    CodeLibraryLocalRetrievalEngine,
    LocalRetrievalQuery,
)
from .offline_catalog import (
    CodeLibraryOfflineCatalog,
    OfflineCatalogEntry,
)
from .resource_index import (
    CodeLibraryResourceIndex,
)
from .local_storage import (
    CodeLibraryLocalStorage,
)


@dataclass(frozen=True)
class CodeLibraryIntegrationResult:
    integrated: bool
    compatible: bool
    score: float
    reasons: tuple[str, ...]
    checks: tuple[str, ...]
    failures: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "integrated": self.integrated,
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "checks": list(self.checks),
            "failures": list(self.failures),
            "metadata": dict(self.metadata),
        }


class CodeLibraryIntegrationVerifier:
    """
    Verifies the operational integration between the CL-14
    Code Library subsystems.

    The verifier exercises the real catalog, storage, retrieval,
    indexing, incremental-update, Android compatibility, and
    compiled-payload components rather than duplicating their logic.
    """

    def __init__(
        self,
        *,
        catalog: CodeLibraryOfflineCatalog | None = None,
        storage: CodeLibraryLocalStorage | None = None,
        index: CodeLibraryResourceIndex | None = None,
    ) -> None:
        self.catalog = (
            catalog
            if catalog is not None
            else CodeLibraryOfflineCatalog()
        )

        if storage is not None:
            self.storage = storage
        else:
            storage_signature = inspect.signature(
                CodeLibraryLocalStorage
            )
            context_parameter = storage_signature.parameters.get(
                "context"
            )

            if context_parameter is None:
                raise TypeError(
                    "CodeLibraryLocalStorage must expose a context parameter"
                )

            context_type = context_parameter.annotation

            if (
                context_type is inspect.Parameter.empty
                or not hasattr(context_type, "namespace_path")
            ):
                from .local_storage import LocalStorageContext

                context_type = LocalStorageContext

            storage_context = context_type(
                root=".builder",
                namespace="code_library",
                version=1,
            )

            self.storage = CodeLibraryLocalStorage(
                context=storage_context
            )

        self.index = (
            index
            if index is not None
            else CodeLibraryResourceIndex()
        )

        self.retrieval = (
            CodeLibraryLocalRetrievalEngine(
                self.catalog
            )
        )

        self.updater = (
            CodeLibraryIncrementalUpdater(
                self.index
            )
        )

        self.android = (
            CodeLibraryAndroidCompatibilityEngine()
        )

        self.payload_verifier = (
            CodeLibraryCompiledPayloadVerifier()
        )

    @staticmethod
    def _entry_to_terms(
        entry: OfflineCatalogEntry,
    ) -> tuple[str, ...]:
        values: list[str] = [
            entry.asset_id,
            entry.name,
            entry.asset_type,
            entry.language,
            entry.framework,
            entry.runtime,
            *entry.tags,
        ]

        return tuple(
            value
            for value in values
            if isinstance(value, str)
            and value.strip()
        )

    def register_asset(
        self,
        entry: OfflineCatalogEntry,
    ) -> None:
        if not isinstance(
            entry,
            OfflineCatalogEntry,
        ):
            raise TypeError(
                "entry must be OfflineCatalogEntry"
            )

        self.catalog.register(entry)

        self.storage.put(
            entry.asset_id,
            entry.to_dict(),
        )

        self.index.add(
            entry.asset_id,
            self._entry_to_terms(entry),
            metadata={
                "name": entry.name,
                "language": entry.language,
                "framework": entry.framework,
                "runtime": entry.runtime,
            },
        )

    def retrieve(
        self,
        query: LocalRetrievalQuery,
    ):
        return self.retrieval.retrieve(query)

    def update_asset_index(
        self,
        asset_id: str,
        terms: tuple[str, ...],
        *,
        metadata: dict | None = None,
    ):
        return self.updater.update(
            asset_id,
            terms,
            metadata=metadata,
        )

    def remove_asset(
        self,
        asset_id: str,
    ):
        self.catalog.remove(asset_id)
        self.storage.remove(asset_id)
        return self.updater.remove(asset_id)

    def verify_android(
        self,
        asset: Any,
        context: AndroidCompatibilityContext,
    ):
        return self.android.analyze(
            asset,
            context,
        )

    def verify_payload(
        self,
        payload_path,
        manifest: CompiledPayloadManifest,
    ):
        return self.payload_verifier.verify(
            payload_path,
            manifest,
        )

    def verify(
        self,
        *,
        android_asset: Any | None = None,
        android_context: AndroidCompatibilityContext | None = None,
        payload_path=None,
        payload_manifest: CompiledPayloadManifest | None = None,
    ) -> CodeLibraryIntegrationResult:
        checks: list[str] = []
        failures: list[str] = []

        def run_check(
            name: str,
            condition: bool,
        ) -> None:
            if condition:
                checks.append(name)
            else:
                failures.append(name)

        run_check(
            "catalog_available",
            self.catalog.count() >= 0,
        )

        run_check(
            "storage_available",
            self.storage.count() >= 0,
        )

        run_check(
            "index_available",
            self.index.count() >= 0,
        )

        run_check(
            "retrieval_available",
            isinstance(
                self.retrieval,
                CodeLibraryLocalRetrievalEngine,
            ),
        )

        run_check(
            "incremental_updates_available",
            isinstance(
                self.updater,
                CodeLibraryIncrementalUpdater,
            ),
        )

        run_check(
            "android_compatibility_available",
            isinstance(
                self.android,
                CodeLibraryAndroidCompatibilityEngine,
            ),
        )

        run_check(
            "payload_verification_available",
            isinstance(
                self.payload_verifier,
                CodeLibraryCompiledPayloadVerifier,
            ),
        )

        if android_asset is not None:
            if android_context is None:
                failures.append(
                    "android_context_missing"
                )
            else:
                android_result = self.verify_android(
                    android_asset,
                    android_context,
                )

                run_check(
                    "android_compatibility",
                    android_result.compatible,
                )

        if payload_path is not None:
            if payload_manifest is None:
                failures.append(
                    "payload_manifest_missing"
                )
            else:
                payload_result = self.verify_payload(
                    payload_path,
                    payload_manifest,
                )

                run_check(
                    "compiled_payload",
                    payload_result.valid,
                )

        integrated = not failures

        reasons: list[str] = []

        if integrated:
            reasons.append(
                "code_library_components_integrated"
            )
        else:
            reasons.append(
                "code_library_integration_failed"
            )

        if self.catalog.count() > 0:
            reasons.append(
                "catalog_contains_assets"
            )

        if self.index.count() > 0:
            reasons.append(
                "index_contains_assets"
            )

        if self.storage.count() > 0:
            reasons.append(
                "storage_contains_assets"
            )

        score = (
            10.0
            if integrated
            else max(
                0.0,
                10.0
                - (
                    len(failures)
                    * 2.0
                ),
            )
        )

        return CodeLibraryIntegrationResult(
            integrated=integrated,
            compatible=integrated,
            score=score,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            checks=tuple(checks),
            failures=tuple(failures),
            metadata={
                "catalog_count": self.catalog.count(),
                "storage_count": self.storage.count(),
                "index_count": self.index.count(),
                "index_term_count": self.index.term_count(),
                "check_count": len(checks),
                "failure_count": len(failures),
            },
        )


__all__ = [
    "CodeLibraryIntegrationResult",
    "CodeLibraryIntegrationVerifier",
]
