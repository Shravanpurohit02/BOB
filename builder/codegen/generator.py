BUILDER_OUTPUT_SPEC = """
You are the Vidhi Builder code generation engine.

You MUST respond with exactly ONE JSON object.

Do NOT write markdown.
Do NOT use code fences.
Do NOT explain.
Do NOT include reasoning.
Do NOT include analysis.
Do NOT include comments.

The JSON MUST conform exactly to:

{
  "schema":"vidhi-builder/v1",
  "directories":[
    {
      "path":"..."
    }
  ],
  "files":[
    {
      "path":"...",
      "action":"create|modify",
      "language":"python",
      "content":"..."
    }
  ],
  "warnings":[]
}

Rules:

- Return ONLY valid JSON.
- schema is mandatory.
- directories and files must always exist.
- warnings must always exist.
- Never emit delete actions.
- Never emit placeholder code.
- Every generated file must compile.
- Every import must resolve.
"""


from builder.codegen.prompt_builder import builder as prompt_builder
from builder.codegen.prompts import SYSTEM_PROMPT
from builder.context import engine as context_engine
from builder.context.selector import selector as context_selector
from builder.providers.execution import ExecutionRequest, engine
from builder.providers.runtime.context_budget import engine as budget_engine


class CodeGenerator:
    def generate(self, request):

        budget = budget_engine.budget(
            provider="",
            model=request.model,
        )

        if "audit" in request.instruction.lower():
            semantic_context = context_engine.create(
                workspace=request.workspace,
                objective=request.instruction,
                budget=budget.available_input_tokens,
            )

        else:
            semantic_context = context_selector.build_prompt_context(
                workspace=request.workspace,
                objective=request.instruction,
                budget=budget.available_input_tokens,
            )

            if not semantic_context.strip():
                semantic_context = context_engine.create(
                    workspace=request.workspace,
                    objective=request.instruction,
                    budget=budget.available_input_tokens,
                )


        engineering_context = f"""
ENGINEERING PLAN

Risk
----
{request.risk}

Resolved Files
--------------
{chr(10).join(request.resolved_files) if request.resolved_files else "(none)"}

Execution Order
---------------
{chr(10).join(request.execution_order) if request.execution_order else "(none)"}

Resolved Symbols
----------------
{chr(10).join(str(s) for s in request.resolved_symbols) if request.resolved_symbols else "(none)"}

Operations
----------
{chr(10).join(str(o) for o in request.operations) if request.operations else "(none)"}

Impacts
-------
{chr(10).join(str(i) for i in request.impacts) if request.impacts else "(none)"}

Engineering Rules
-----------------
Modify ONLY the planned files.
Do NOT invent unrelated files.
Respect the operation plan.
Create files ONLY if the operation plan requires it.
Preserve existing architecture.
"""

        messages = prompt_builder.build(
            system_prompt=(BUILDER_OUTPUT_SPEC + "\n\n" + SYSTEM_PROMPT),
            objective=request.instruction,
            repository_context=semantic_context,
            additional_context=request.context + "\n\n" + engineering_context,
            context_budget=budget.available_input_tokens,
        )

        execution = ExecutionRequest(
            model=request.model,
            messages=messages,
        )

        return engine.execute(execution)


generator = CodeGenerator()
