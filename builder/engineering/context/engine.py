from .models import EngineeringContext


class ContextEngine:

    def create(
        self,
        objective: str,
        workspace: str = "",
    ):

        return EngineeringContext(
            objective=objective,
            workspace=workspace,
        )

    def add_module(
        self,
        context,
        module,
    ):
        if module not in context.target_modules:
            context.target_modules.append(module)

    def add_file(
        self,
        context,
        path,
    ):
        if path not in context.related_files:
            context.related_files.append(path)

    def add_dependency(
        self,
        context,
        dependency,
    ):
        if dependency not in context.dependencies:
            context.dependencies.append(dependency)

    def add_symbol(
        self,
        context,
        symbol,
    ):
        if symbol not in context.symbols:
            context.symbols.append(symbol)


engine = ContextEngine()
