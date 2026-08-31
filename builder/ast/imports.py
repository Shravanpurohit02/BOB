from __future__ import annotations

from collections import defaultdict

from builder.ast.module import Module


class ImportIndex:
    """
    Builds a forward dependency graph from parsed modules.

    Output format:
        {
            "a.py": ["b.py", "c.py"],
            ...
        }
    """

    def build(
        self,
        modules: list[Module],
    ) -> dict[str, list[str]]:

        module_names: dict[str, str] = {}

        for module in modules:
            module_names[module.name] = module.path

            if module.qualified_name:
                module_names[module.qualified_name] = module.path

        forward: dict[str, list[str]] = defaultdict(list)

        for module in modules:
            deps: set[str] = set()

            for imp in module.imports:
                target = module_names.get(imp)

                if target and target != module.path:
                    deps.add(target)

            for imp in module.import_from:
                target = module_names.get(imp)

                if target and target != module.path:
                    deps.add(target)

            forward[module.path] = sorted(deps)

        return dict(forward)

    def dependencies(
        self,
        module: Module,
        modules: list[Module],
    ) -> list[str]:

        return self.build(modules).get(
            module.path,
            [],
        )

    def reverse(
        self,
        modules: list[Module],
    ) -> dict[str, list[str]]:

        reverse: dict[str, list[str]] = defaultdict(list)

        forward = self.build(modules)

        for source, targets in forward.items():
            for target in targets:
                reverse[target].append(source)

        return {k: sorted(v) for k, v in reverse.items()}


imports = ImportIndex()
