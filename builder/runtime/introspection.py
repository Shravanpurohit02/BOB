from __future__ import annotations

from builder.project.analyzer import analyzer
from builder.reflection.query import query
from builder.runtime.manifest import RuntimeManifest


class RuntimeIntrospection:
    """
    Collects runtime information about a Builder workspace.
    """

    def inspect(
        self,
        workspace: str,
    ) -> RuntimeManifest:

        stats = analyzer.statistics(workspace)

        manifest = RuntimeManifest(
            workspace=workspace,
            modules=stats["modules"],
            files=stats["files"],
            packages=stats["packages"],
        )

        manifest.metadata.update(
            {
                "classes": len(
                    query.classes(workspace)
                ),
                "functions": len(
                    query.functions(workspace)
                ),
                "symbols": len(
                    query.symbols(workspace)
                ),
            }
        )

        return manifest

    def summary(
        self,
        workspace: str,
    ) -> dict:

        return self.inspect(
            workspace
        ).to_dict()


introspection = RuntimeIntrospection()

