from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .composition_planning import (
    CompositionPlan,
    CompositionPlanContext,
    CodeLibraryCompositionPlanningEngine,
)
from .dependency_graph import (
    CodeLibraryDependencyGraphEngine,
    DependencyGraphContext,
)
from .engine import CodeLibraryEngine


@dataclass(frozen=True)
class AssemblyUnit:
    """One executable assembly unit in dependency order."""

    asset_id: str
    order: int
    dependencies: tuple[str, ...] = ()
    dependents: tuple[str, ...] = ()
    asset_type: str = ""
    name: str = ""
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "order": self.order,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "asset_type": self.asset_type,
            "name": self.name,
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class AssemblyPlan:
    """Resolved dependency-aware assembly plan."""

    units: tuple[AssemblyUnit, ...]
    asset_ids: tuple[str, ...]
    dependency_order: tuple[str, ...]
    unresolved_dependencies: tuple[str, ...] = ()
    cycles: tuple[tuple[str, ...], ...] = ()
    assembled: bool = False
    compatible: bool = False
    score: float = 0.0
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "units": [unit.to_dict() for unit in self.units],
            "asset_ids": list(self.asset_ids),
            "dependency_order": list(self.dependency_order),
            "unresolved_dependencies": list(
                self.unresolved_dependencies
            ),
            "cycles": [list(cycle) for cycle in self.cycles],
            "assembled": self.assembled,
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata or {}),
        }


class CodeLibraryAssemblyPlanningEngine:
    """Resolves a composition plan into an assembly-ready dependency order."""

    def __init__(
        self,
        engine: CodeLibraryEngine | None = None,
    ) -> None:
        self.engine = engine or CodeLibraryEngine()
        self.composition = (
            CodeLibraryCompositionPlanningEngine(
                self.engine
            )
        )
        self.graph = (
            CodeLibraryDependencyGraphEngine(
                self.engine
            )
        )

    def assemble(
        self,
        asset_ids: tuple[str, ...],
        context: CompositionPlanContext | None = None,
    ) -> AssemblyPlan:
        context = context or CompositionPlanContext()

        unique_ids = tuple(dict.fromkeys(asset_ids))

        for asset_id in unique_ids:
            if self.engine.get(asset_id) is None:
                raise ValueError(
                    f"Code Library asset not found: {asset_id}"
                )

        requested_set = set(unique_ids)
        existing_set = set(context.asset_ids)
        project_dependencies = set(context.dependencies)

        composition = self.composition.plan(
            unique_ids,
            CompositionPlanContext(
                asset_ids=context.asset_ids,
                language=context.language,
                framework=context.framework,
                runtime=context.runtime,
                asset_type=context.asset_type,
                capabilities=context.capabilities,
                dependencies=context.dependencies,
            ),
        )

        graph = self.graph.build(
            DependencyGraphContext(
                project_dependencies=context.dependencies,
            )
        )

        graph_nodes = {
            node.asset_id: node
            for node in graph.nodes
        }

        selected_ids = []
        review_ids = []
        rejected_ids = []

        for asset_id in unique_ids:
            asset = self.engine.get(asset_id)

            if asset is None:
                continue

            if asset_id in existing_set:
                rejected_ids.append(asset_id)
                continue

            node = graph_nodes.get(asset_id)

            if node is None:
                rejected_ids.append(asset_id)
                continue

            unresolved_external = [
                dependency
                for dependency in node.missing_dependencies
                if dependency not in project_dependencies
                and dependency not in existing_set
                and dependency not in requested_set
            ]

            if unresolved_external:
                review_ids.append(asset_id)
                continue

            selected_ids.append(asset_id)

        selected = tuple(selected_ids)
        selected_set = set(selected)

        unresolved = set()

        for asset_id in selected:
            node = graph_nodes.get(asset_id)

            if node is None:
                continue

            for dependency in node.missing_dependencies:
                if (
                    dependency not in project_dependencies
                    and dependency not in existing_set
                    and dependency not in requested_set
                ):
                    unresolved.add(dependency)

        selected_graph_nodes = {
            asset_id: graph_nodes[asset_id]
            for asset_id in selected
            if asset_id in graph_nodes
        }

        dependency_order = self._topological_order(
            selected_graph_nodes
        )

        cycles = tuple(
            cycle
            for cycle in graph.cycles
            if any(
                member in selected_set
                for member in cycle
            )
        )

        units = []

        for order, asset_id in enumerate(
            dependency_order,
            start=1,
        ):
            asset = self.engine.get(asset_id)
            node = selected_graph_nodes[asset_id]

            units.append(
                AssemblyUnit(
                    asset_id=asset_id,
                    order=order,
                    dependencies=tuple(
                        dependency
                        for dependency in node.dependencies
                        if dependency in selected_set
                    ),
                    dependents=tuple(
                        dependent
                        for dependent in node.dependents
                        if dependent in selected_set
                    ),
                    asset_type=(
                        asset.asset_type
                        if asset is not None
                        else ""
                    ),
                    name=(
                        asset.name
                        if asset is not None
                        else ""
                    ),
                    metadata={
                        "language": (
                            asset.language
                            if asset is not None
                            else ""
                        ),
                        "framework": (
                            asset.framework
                            if asset is not None
                            else ""
                        ),
                        "runtime": (
                            asset.runtime
                            if asset is not None
                            else ""
                        ),
                        "version": (
                            asset.version
                            if asset is not None
                            else ""
                        ),
                        "lifecycle": (
                            asset.lifecycle
                            if asset is not None
                            else ""
                        ),
                    },
                )
            )

        reasons = []

        if selected:
            reasons.append("composition_assets_resolved")

        if dependency_order:
            reasons.append("dependency_order_resolved")

        if unresolved:
            reasons.append("unresolved_dependencies")

        if cycles:
            reasons.append("dependency_cycle_detected")

        if review_ids:
            reasons.append("composition_review_required")

        if rejected_ids:
            reasons.append("composition_rejections_present")

        assembled = bool(
            selected
            and dependency_order
            and not unresolved
            and not cycles
            and not review_ids
            and not rejected_ids
        )

        if assembled:
            reasons.append("assembly_ready")
        else:
            reasons.append("assembly_blocked")

        compatible = bool(
            selected
            and not unresolved
            and not cycles
            and not review_ids
            and not rejected_ids
        )

        score = self._score(
            composition,
            unresolved,
            cycles,
            tuple(review_ids),
            tuple(rejected_ids),
        )

        if compatible and score == 0.0:
            score = 10.0

        return AssemblyPlan(
            units=tuple(units),
            asset_ids=selected,
            dependency_order=dependency_order,
            unresolved_dependencies=tuple(sorted(unresolved)),
            cycles=cycles,
            assembled=assembled,
            compatible=compatible,
            score=score,
            reasons=tuple(dict.fromkeys(reasons)),
            metadata={
                "requested_asset_count": len(unique_ids),
                "selected_asset_count": len(selected),
                "unit_count": len(units),
                "cycle_count": len(cycles),
                "unresolved_dependency_count": len(unresolved),
            },
        )

    def assemble_all(
        self,
        context: CompositionPlanContext | None = None,
    ) -> AssemblyPlan:
        context = context or CompositionPlanContext()

        return self.assemble(
            tuple(
                asset.id
                for asset in self.engine.list_assets()
            ),
            context,
        )

    @staticmethod
    def _topological_order(
        nodes: dict[str, Any],
    ) -> tuple[str, ...]:
        remaining = set(nodes)
        dependencies = {
            asset_id: {
                dependency
                for dependency in node.dependencies
                if dependency in nodes
            }
            for asset_id, node in nodes.items()
        }

        ordered: list[str] = []

        while remaining:
            ready = sorted(
                asset_id
                for asset_id in remaining
                if not (
                    dependencies[asset_id]
                    & remaining
                )
            )

            if not ready:
                # Cyclic graphs are reported separately. Preserve a
                # deterministic fallback order rather than looping.
                ready = [min(remaining)]

            for asset_id in ready:
                ordered.append(asset_id)
                remaining.remove(asset_id)

        return tuple(ordered)

    @staticmethod
    def _score(
        composition: CompositionPlan,
        unresolved: set[str],
        cycles: tuple[tuple[str, ...], ...],
        review_ids: tuple[str, ...] = (),
        rejected_ids: tuple[str, ...] = (),
    ) -> float:
        if not composition.selected_asset_ids:
            return 0.0

        score = composition.score

        if unresolved:
            score *= 0.5

        if cycles:
            score *= 0.25

        if review_ids:
            score *= 0.75

        if rejected_ids:
            score *= 0.5

        return round(
            max(0.0, min(10.0, score)),
            6,
        )


assembly_planning = (
    CodeLibraryAssemblyPlanningEngine()
)


__all__ = (
    "AssemblyUnit",
    "AssemblyPlan",
    "CodeLibraryAssemblyPlanningEngine",
    "assembly_planning",
)
