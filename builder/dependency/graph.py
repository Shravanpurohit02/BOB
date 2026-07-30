class DependencyGraph:

    def build(self, packages):

        return {
            package: []
            for package in packages
        }

graph = DependencyGraph()
