from builder.codegen import (
    CodeGenerationRequest,
    engine,
)
from builder.context import engine as context


class Generator:

    def generate(
        self,
        workspace,
        target,
        objective,
    ):

        grounded_context = context.create(
            workspace=workspace,
            objective=objective,
            target_file=target,
        )

        request = CodeGenerationRequest(
            instruction=objective,
            context=grounded_context,
        )

        return engine.generate(request)


generator = Generator()
