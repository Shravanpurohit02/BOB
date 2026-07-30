from builder.codegen import (
    CodeGenerationRequest,
    engine,
)

class Generator:

    def improve(self, improvement):

        return engine.generate(
            CodeGenerationRequest(
                instruction=f"""
Improve this file.

Issue:
{improvement.issue}

Task:
{improvement.proposal}

Return only production-ready code.
""",
            )
        )

generator = Generator()
