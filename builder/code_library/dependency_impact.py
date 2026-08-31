from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dependency_graph import (
    CodeLibraryDependencyGraphEngine,
    DependencyGraphContext,
)
from .engine import CodeLibraryEngine


@dataclass(frozen=True)
class DependencyImpactResult:
    """Impact analysis for removing or changing one asset."""

    asset_id: str
    direct_dependents: tuple[str, ...] = ()
    transitive_dependents: tuple[str, ...] = ()
    affected_assets: tuple[str, ...] = ()
    affected_count: int = 0
    critical: bool = False
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "direct_dependents": list(self.direct_dependents),
            "transitive_dependents": list(
                self.transitive_dependents
            ),
            "affected_assets": list(self.affected_assets),
            "affected_count": self.affected_count,
            "critical": self.critical,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryDependencyImpactEngine:
    """Calculates direct and transitive dependency impact."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.graph = CodeLibraryDependencyGraphEngine(
            self.engine
        )

    def analyze(
        self,
        asset_id: str,
        context: DependencyGraphContext | None = None,
    ) -> DependencyImpactResult:
        asset = self.engine.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        graph = self.graph.build(context)

        node_map = {
            node.asset_id: node
            for node in graph.nodes
        }

        node = node_map.get(asset_id)

        if node is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        direct = tuple(
            sorted(node.dependents)
        )

        transitive = self._transitive_dependents(
            asset_id,
            node_map,
        )

        affected = tuple(
            sorted(
                set(direct) | set(transitive)
            )
        )

        reasons: list[str] = []

        if direct:
            reasons.append("direct_dependents_present")

        if transitive:
            reasons.append("transitive_dependents_present")

        if affected:
            reasons.append("downstream_impact_detected")
        else:
            reasons.append("no_downstream_impact")

        if graph.cycles:
            impacted_cycles = [
                cycle
                for cycle in graph.cycles
                if asset_id in cycle
                or any(
                    member in affected
                    for member in cycle
                )
            ]

            if impacted_cycles:
                reasons.append("cycle_impact_detected")

        critical = (
            len(affected) >= 3
            or bool(
                graph.cycles
                and any(
                    member in affected
                    or member == asset_id
                    for cycle in graph.cycles
                    for member in cycle
                )
            )
        )

        if critical:
            reasons.append("critical_downstream_impact")

        return DependencyImpactResult(
            asset_id=asset_id,
            direct_dependents=direct,
            transitive_dependents=transitive,
            affected_assets=affected,
            affected_count=len(affected),
            critical=critical,
            reasons=tuple(
                dict.fromkeys(reasons)
            ),
            metadata={
                "name": asset.name,
                "asset_type": asset.asset_type,
                "language": asset.language,
                "framework": asset.framework,
                "runtime": asset.runtime,
                "version": asset.version,
                "lifecycle": asset.lifecycle,
            },
        )

    def analyze_many(
        self,
        asset_ids: tuple[str, ...],
        context: DependencyGraphContext | None = None,
    ) -> tuple[DependencyImpactResult, ...]:
        results = tuple(
            self.analyze(asset_id, context)
            for asset_id in dict.fromkeys(asset_ids)
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    -item.affected_count,
                    item.asset_id,
                ),
            )
        )

    def highest_impact(
        self,
        context: DependencyGraphContext | None = None,
    ) -> tuple[DependencyImpactResult, ...]:
        results = tuple(
            self.analyze(
                asset.id,
                context,
            )
            for asset in self.engine.list_assets()
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    -item.affected_count,
                    item.asset_id,
                ),
            )
        )

    @staticmethod
    def _transitive_dependents(
        asset_id: str,
        node_map: dict[str, Any],
    ) -> tuple[str, ...]:
        visited: set[str] = set()
        queue = list(
            node_map[asset_id].dependents
        )

        while queue:
            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            node = node_map.get(current)

            if node is not None:
                queue.extend(
                    node.dependents
                )

        return tuple(
            sorted(visited)
        )


dependency_impact = CodeLibraryDependencyImpactEngine()


__all__ = (
    "DependencyImpactResult",
    "CodeLibraryDependencyImpactEngine",
    "dependency_impact",
)
