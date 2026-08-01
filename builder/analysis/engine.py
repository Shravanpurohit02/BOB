from builder.analysis.prompt import ANALYSIS_SYSTEM_PROMPT
from builder.context import engine as context_engine
from builder.providers.chat.messages import Message
from builder.providers.execution import ExecutionMode, ExecutionRequest
from builder.providers.execution import engine as execution_engine


class AnalysisEngine:
    def analyze(
        self,
        *,
        workspace: str,
        objective: str,
        model: str = "",
    ):
        context = context_engine.create(
            workspace=workspace,
            objective=objective,
            budget=12000,
        )

        request = ExecutionRequest(
            model=model,
            mode=ExecutionMode.CHAT,
            messages=[
                Message(
                    role="system",
                    content=ANALYSIS_SYSTEM_PROMPT,
                ),
                Message(
                    role="user",
                    content=f"""OBJECTIVE

{objective}

REPOSITORY CONTEXT

{context}
""",
                ),
            ],
        )

        return execution_engine.execute(request)


engine = AnalysisEngine()
