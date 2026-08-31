from __future__ import annotations

from dataclasses import dataclass

from .asset_selection import (
    AssetSelectionResult,
)


@dataclass(frozen=True)
class ArchitectureUnit:
    asset_id: str
    order: int
    dependencies: tuple[str, ...] = ()
    dependents: tuple[str, ...] = ()
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.asset_id.strip():
            raise ValueError(
                "asset_id must not be empty"
            )

        if self.order < 1:
            raise ValueError(
                "order must be >= 1"
            )

        object.__setattr__(
            self,
            "dependencies",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip()
                        for value in self.dependencies
                        if isinstance(value, str)
                        and value.strip()
                    )
                )
            ),
        )

        object.__setattr__(
            self,
            "dependents",
            tuple(
                sorted(
                    dict.fromkeys(
                        value.strip()
                        for value in self.dependents
                        if isinstance(value, str)
                        and value.strip()
                    )
                )
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata or {}),
        )

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "order": self.order,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class ArchitectureCompositionResult:
    requirement_name: str
    units: tuple[ArchitectureUnit, ...]
    dependency_order: tuple[str, ...]
    unresolved_dependencies: tuple[str, ...]
    cycles: tuple[tuple[str, ...], ...]
    composed: bool
    compatible: bool
    score: float
    reasons: tuple[str, ...]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "requirement_name": self.requirement_name,
            "units": [
                unit.to_dict()
                for unit in self.units
            ],
            "dependency_order": list(
                self.dependency_order
            ),
            "unresolved_dependencies": list(
                self.unresolved_dependencies
            ),
            "cycles": [
                list(cycle)
                for cycle in self.cycles
            ],
            "composed": self.composed,
            "compatible": self.compatible,
            "score": self.score,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


class CodeLibraryArchitectureComposer:
    """
    Converts CL-15.3 selected assets into a deterministic dependency-aware
    architecture.

    Dependencies are resolved only against the selected asset set.
    External/unselected dependencies are reported as unresolved rather
    than silently invented.
    """

    @staticmethod
    def _asset_id(asset) -> str:
        value = getattr(asset, "asset_id", "")
        return (
            value.strip()
            if isinstance(value, str)
            else ""
        )

    @staticmethod
    def _dependencies(asset) -> tuple[str, ...]:
        values = getattr(
            asset,
            "dependencies",
            (),
        )

        if not values:
            return ()

        return tuple(
            sorted(
                dict.fromkeys(
                    value.strip()
                    for value in values
                    if isinstance(value, str)
                    and value.strip()
                )
            )
        )

    @staticmethod
    def _detect_cycles(
        dependency_map: dict[str, tuple[str, ...]],
    ) -> tuple[tuple[str, ...], ...]:
        cycles: set[tuple[str, ...]] = set()
        visiting: list[str] = []
        visiting_set: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting_set:
                index = visiting.index(node)
                cycle = tuple(
                    visiting[index:]
                )
                if cycle:
                    cycles.add(
                        tuple(
                            sorted(cycle)
                        )
                    )
                return

            if node in visited:
                return

            visiting.append(node)
            visiting_set.add(node)

            for dependency in dependency_map.get(
                node,
                (),
            ):
                if dependency in dependency_map:
                    visit(dependency)

            visiting.pop()
            visiting_set.remove(node)
            visited.add(node)

        for node in sorted(
            dependency_map
        ):
            visit(node)

        return tuple(
            sorted(cycles)
        )

    @staticmethod
    def _topological_order(
        dependency_map: dict[str, tuple[str, ...]],
    ) -> tuple[str, ...]:
        indegree = {
            node: 0
            for node in dependency_map
        }

        dependents: dict[str, list[str]] = {
            node: []
            for node in dependency_map
        }

        for node, dependencies in dependency_map.items():
            for dependency in dependencies:
                if dependency in indegree:
                    indegree[node] += 1
                    dependents[dependency].append(
                        node
                    )

        ready = sorted(
            node
            for node, degree in indegree.items()
            if degree == 0
        )

        order: list[str] = []

        while ready:
            node = ready.pop(0)
            order.append(node)

            for dependent in sorted(
                dependents[node]
            ):
                indegree[dependent] -= 1

                if indegree[dependent] == 0:
                    ready.append(dependent)
                    ready.sort()

        return tuple(order)

    def compose(
        self,
        result: AssetSelectionResult,
    ) -> ArchitectureCompositionResult:
        if not isinstance(
            result,
            AssetSelectionResult,
        ):
            raise TypeError(
                "result must be AssetSelectionResult"
            )

        assets = tuple(
            result.selected_assets
        )

        asset_map: dict[str, object] = {}

        for asset in assets:
            asset_id = self._asset_id(asset)

            if not asset_id:
                continue

            asset_map.setdefault(
                asset_id,
                asset,
            )

        dependency_map: dict[
            str,
            tuple[str, ...],
        ] = {}

        unresolved: set[str] = set()

        for asset_id, asset in asset_map.items():
            dependencies = self._dependencies(
                asset
            )

            dependency_map[asset_id] = dependencies

            for dependency in dependencies:
                if dependency not in asset_map:
                    unresolved.add(
                        dependency
                    )

        cycles = self._detect_cycles(
            dependency_map
        )

        dependency_order = self._topological_order(
            dependency_map
        )

        order_index = {
            asset_id: index + 1
            for index, asset_id
            in enumerate(dependency_order)
        }

        dependents_map: dict[
            str,
            list[str],
        ] = {
            asset_id: []
            for asset_id in asset_map
        }

        for asset_id, dependencies in dependency_map.items():
            for dependency in dependencies:
                if dependency in dependents_map:
                    dependents_map[
                        dependency
                    ].append(asset_id)

        units: list[ArchitectureUnit] = []

        for asset_id in dependency_order:
            units.append(
                ArchitectureUnit(
                    asset_id=asset_id,
                    order=order_index[
                        asset_id
                    ],
                    dependencies=dependency_map[
                        asset_id
                    ],
                    dependents=tuple(
                        sorted(
                            dependents_map[
                                asset_id
                            ]
                        )
                    ),
                    metadata={
                        "selected": True,
                    },
                )
            )

        composed = (
            bool(asset_map)
            and not unresolved
            and not cycles
            and len(dependency_order)
            == len(asset_map)
        )

        reasons: list[str] = []

        if asset_map:
            reasons.append(
                "selected_assets_received"
            )
        else:
            reasons.append(
                "no_selected_assets"
            )

        if not unresolved:
            reasons.append(
                "dependencies_resolved"
            )
        else:
            reasons.append(
                "unresolved_dependencies_detected"
            )

        if not cycles:
            reasons.append(
                "dependency_graph_acyclic"
            )
        else:
            reasons.append(
                "dependency_cycle_detected"
            )

        if composed:
            reasons.append(
                "architecture_composed"
            )
        else:
            reasons.append(
                "architecture_composition_blocked"
            )

        score = (
            10.0
            if composed
            else max(
                0.0,
                10.0
                - (
                    len(unresolved) * 2.0
                )
                - (
                    len(cycles) * 4.0
                ),
            )
        )

        return ArchitectureCompositionResult(
            requirement_name=result.requirement_name,
            units=tuple(units),
            dependency_order=dependency_order,
            unresolved_dependencies=tuple(
                sorted(unresolved)
            ),
            cycles=cycles,
            composed=composed,
            compatible=composed,
            score=score,
            reasons=tuple(
                reasons
            ),
            metadata={
                "selected_asset_count": len(
                    assets
                ),
                "unit_count": len(
                    units
                ),
                "unresolved_dependency_count": len(
                    unresolved
                ),
                "cycle_count": len(
                    cycles
                ),
            },
        )

    def compose_selected(
        self,
        result: AssetSelectionResult,
    ) -> ArchitectureCompositionResult:
        return self.compose(result)


__all__ = [
    "ArchitectureUnit",
    "ArchitectureCompositionResult",
    "CodeLibraryArchitectureComposer",
]
