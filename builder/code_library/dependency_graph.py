from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import CodeLibraryEngine
from .models import CodeAsset


@dataclass(frozen=True)
class DependencyGraphContext:
    """Optional project dependencies used to build a dependency graph."""

    project_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class DependencyGraphNode:
    """A node in the Code Library dependency graph."""

    asset_id: str
    dependencies: tuple[str, ...] = ()
    dependents: tuple[str, ...] = ()
    missing_dependencies: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "missing_dependencies": list(self.missing_dependencies),
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class DependencyGraphResult:
    """Complete dependency graph analysis."""

    nodes: tuple[DependencyGraphNode, ...]
    roots: tuple[str, ...]
    leaves: tuple[str, ...]
    missing_dependencies: tuple[str, ...]
    cycles: tuple[tuple[str, ...], ...]
    asset_count: int
    edge_count: int

    @property
    def acyclic(self) -> bool:
        return not self.cycles

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "roots": list(self.roots),
            "leaves": list(self.leaves),
            "missing_dependencies": list(
                self.missing_dependencies
            ),
            "cycles": [list(cycle) for cycle in self.cycles],
            "asset_count": self.asset_count,
            "edge_count": self.edge_count,
            "acyclic": self.acyclic,
        }


class CodeLibraryDependencyGraphEngine:
    """Builds and analyzes dependency relationships between assets."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()

    def build(
        self,
        context: DependencyGraphContext | None = None,
    ) -> DependencyGraphResult:
        context = context or DependencyGraphContext()

        assets = self.engine.list_assets()
        asset_map = {
            asset.id: asset
            for asset in assets
        }

        dependency_to_assets: dict[str, set[str]] = {
            asset_id: set()
            for asset_id in asset_map
        }

        node_dependencies: dict[str, tuple[str, ...]] = {}
        missing: set[str] = set()
        edge_count = 0

        project_dependencies = {
            value.strip().lower()
            for value in context.project_dependencies
            if value.strip()
        }

        for asset in assets:
            dependencies = tuple(
                dict.fromkeys(
                    dependency.strip().lower()
                    for dependency in asset.dependencies
                    if dependency.strip()
                )
            )

            node_dependencies[asset.id] = dependencies

            for dependency in dependencies:
                matching_asset = self._find_dependency_asset(
                    dependency,
                    asset_map,
                )

                if matching_asset is not None:
                    dependency_to_assets[
                        matching_asset.id
                    ].add(asset.id)
                    edge_count += 1
                elif dependency not in project_dependencies:
                    missing.add(dependency)

        nodes: list[DependencyGraphNode] = []

        for asset in assets:
            dependencies = node_dependencies[asset.id]

            resolved_dependencies = tuple(
                sorted(
                    resolved.id
                    for dependency in dependencies
                    for resolved in (
                        self._find_dependency_asset(
                            dependency,
                            asset_map,
                        ),
                    )
                    if resolved is not None
                )
            )

            missing_dependencies = tuple(
                sorted(
                    dependency
                    for dependency in dependencies
                    if self._find_dependency_asset(
                        dependency,
                        asset_map,
                    )
                    is None
                    and dependency not in project_dependencies
                )
            )

            nodes.append(
                DependencyGraphNode(
                    asset_id=asset.id,
                    dependencies=resolved_dependencies,
                    dependents=tuple(
                        sorted(
                            dependency_to_assets[asset.id]
                        )
                    ),
                    missing_dependencies=missing_dependencies,
                    metadata=self._metadata(asset),
                )
            )

        node_map = {
            node.asset_id: node
            for node in nodes
        }

        roots = tuple(
            sorted(
                node.asset_id
                for node in nodes
                if not node.dependencies
            )
        )

        leaves = tuple(
            sorted(
                node.asset_id
                for node in nodes
                if not node.dependents
            )
        )

        cycles = self._detect_cycles(node_map)

        return DependencyGraphResult(
            nodes=tuple(nodes),
            roots=roots,
            leaves=leaves,
            missing_dependencies=tuple(sorted(missing)),
            cycles=cycles,
            asset_count=len(nodes),
            edge_count=edge_count,
        )

    def graph_for_asset(
        self,
        asset_id: str,
        context: DependencyGraphContext | None = None,
    ) -> DependencyGraphResult:
        if self.engine.get(asset_id) is None:
            raise ValueError(
                f"Code Library asset not found: {asset_id}"
            )

        return self.build(context)

    def dependencies_of(
        self,
        asset_id: str,
        context: DependencyGraphContext | None = None,
    ) -> tuple[str, ...]:
        result = self.graph_for_asset(asset_id, context)

        for node in result.nodes:
            if node.asset_id == asset_id:
                return node.dependencies

        return ()

    def dependents_of(
        self,
        asset_id: str,
        context: DependencyGraphContext | None = None,
    ) -> tuple[str, ...]:
        result = self.graph_for_asset(asset_id, context)

        for node in result.nodes:
            if node.asset_id == asset_id:
                return node.dependents

        return ()

    @staticmethod
    def _find_dependency_asset(
        dependency: str,
        asset_map: dict[str, CodeAsset],
    ) -> CodeAsset | None:
        normalized = dependency.strip().lower()

        for asset in asset_map.values():
            if asset.id.lower() == normalized:
                return asset

            if asset.name.strip().lower() == normalized:
                return asset

        return None

    @staticmethod
    def _detect_cycles(
        node_map: dict[str, DependencyGraphNode],
    ) -> tuple[tuple[str, ...], ...]:
        adjacency = {
            node.asset_id: set(
                node.dependencies
            )
            for node in node_map.values()
        }

        # Dependencies may be package names rather than asset IDs.
        normalized_lookup = {
            asset_id.lower(): asset_id
            for asset_id in node_map
        }

        for asset_id, dependencies in list(
            adjacency.items()
        ):
            resolved: set[str] = set()

            for dependency in dependencies:
                dependency_id = normalized_lookup.get(
                    dependency.lower()
                )

                if dependency_id is not None:
                    resolved.add(dependency_id)

            adjacency[asset_id] = resolved

        cycles: set[tuple[str, ...]] = set()
        visiting: list[str] = []
        active: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in active:
                try:
                    start = visiting.index(node)
                except ValueError:
                    return

                cycle = visiting[start:] + [node]

                # Canonical rotation prevents duplicate cycles.
                body = cycle[:-1]
                if body:
                    rotations = [
                        tuple(
                            body[index:] + body[:index]
                        )
                        for index in range(len(body))
                    ]
                    canonical = min(rotations)
                    cycles.add(canonical)
                return

            if node in visited:
                return

            active.add(node)
            visiting.append(node)

            for dependency in sorted(
                adjacency.get(node, ())
            ):
                visit(dependency)

            visiting.pop()
            active.remove(node)
            visited.add(node)

        for node in sorted(adjacency):
            visit(node)

        return tuple(sorted(cycles))

    @staticmethod
    def _metadata(
        asset: CodeAsset,
    ) -> dict[str, Any]:
        return {
            "name": asset.name,
            "asset_type": asset.asset_type,
            "language": asset.language,
            "framework": asset.framework,
            "runtime": asset.runtime,
            "version": asset.version,
            "lifecycle": asset.lifecycle,
        }


dependency_graph = CodeLibraryDependencyGraphEngine()


__all__ = (
    "DependencyGraphContext",
    "DependencyGraphNode",
    "DependencyGraphResult",
    "CodeLibraryDependencyGraphEngine",
    "dependency_graph",
)
