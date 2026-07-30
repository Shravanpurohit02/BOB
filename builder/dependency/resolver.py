import importlib.util

class Resolver:

    def resolve(self, packages):

        resolved = {}

        for package in packages:
            resolved[package] = (
                importlib.util.find_spec(package)
                is not None
            )

        return resolved

resolver = Resolver()
