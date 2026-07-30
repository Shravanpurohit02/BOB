from builder.dependency.graph import graph
from builder.dependency.resolver import resolver
from builder.dependency.scanner import scanner

class DependencyEngine:

    def analyze(self, workspace: str):

        packages = scanner.scan(workspace)

        return {
            "packages": packages,
            "graph": graph.build(packages),
            "installed": resolver.resolve(packages),
        }

engine = DependencyEngine()
