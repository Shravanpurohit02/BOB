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
from builder.providers.runtime.context_budget import context_budget as budget_engine


class CodeGenerator:
    def generate(self, request):

        budget = budget_engine.build(
            provider="gemini",
            workspace=request.workspace,
            objective=request.instruction,
        )

        if "audit" in request.instruction.lower():
            semantic_context = context_engine.create(
                workspace=request.workspace,
                objective=request.instruction,
                budget=budget.token_limit,
            )

        else:
            semantic_context = context_selector.build_prompt_context(
                workspace=request.workspace,
                objective=request.instruction,
                budget=budget.token_limit,
            )

            if not semantic_context.strip():
                semantic_context = context_engine.create(
                    workspace=request.workspace,
                    objective=request.instruction,
                    budget=budget.token_limit,
                )



        print("=" * 80)
        print("ENGINEERING OBJECT COUNTS")
        print("=" * 80)
        print("resolved_files   :", len(request.resolved_files))
        print("resolved_symbols :", len(request.resolved_symbols))
        print("operations       :", len(request.operations))
        print("impacts          :", len(request.impacts))
        print("execution_order  :", len(request.execution_order))
        print("=" * 80)

        def _size(name, value):
            s = str(value)
            print(f"{name:<18} {len(s.encode('utf-8')):,} bytes")

        _size("resolved_files", request.resolved_files)
        _size("resolved_symbols", request.resolved_symbols)
        _size("operations", request.operations)
        _size("impacts", request.impacts)
        _size("execution_order", request.execution_order)


        resolved_symbols = "\n".join(
            f"- {getattr(s, 'qualified_name', getattr(s, 'name', str(s)))} ({getattr(s, 'kind', '')})"
            for s in request.resolved_symbols
        ) or "(none)"

        operations = "\n".join(
            f"- {getattr(op, 'operation', '?')}: {getattr(op, 'file', '?')}"
            for op in request.operations
        ) or "(none)"

        impacts = "\n".join(
            f"- {i.get('symbol')} | risk={i.get('risk')} | modules={i.get('affected_module_count', len(i.get('affected_modules', [])))}"
            for i in request.impacts
        ) or "(none)"

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
{resolved_symbols}

Operations
----------
{operations}

Impacts
-------
{impacts}

Engineering Rules
-----------------
Modify ONLY the planned files.
Do NOT invent unrelated files.
Respect the operation plan EXACTLY.

Artifact action rules are mandatory:

- create_file     -> action="create"
- modify_file     -> action="modify"
- replace_symbol  -> action="modify"
- insert_symbol   -> action="modify"
- delete_symbol   -> action="modify"
- rename_symbol   -> action="modify"
- delete_file     -> action="delete"
- rename_file     -> action="rename"
- move_file       -> action="move"

For an existing file listed by a modify/replace/insert/rename-symbol
operation, NEVER emit action="create".

If the engineering operation says modify_file and the target file
already exists, the generated artifact MUST use:

"action":"modify"

The action field describes the engineering operation being performed,
not whether the model happened to regenerate the complete file content.

Create files ONLY when the operation plan explicitly contains
create_file.
Preserve existing architecture.
"""



        print("=" * 80)
        print("CONTEXT BREAKDOWN")
        print("=" * 80)
        print("semantic_context :", len(semantic_context.encode("utf-8")))
        print("request.context  :", len(request.context.encode("utf-8")))
        print("engineering_ctx  :", len(engineering_context.encode("utf-8")))
        print("=" * 80)

        messages = prompt_builder.build(

            system_prompt=(BUILDER_OUTPUT_SPEC + "\n\n" + SYSTEM_PROMPT),
            objective=request.instruction,
            repository_context=semantic_context,
            additional_context=request.context + "\n\n" + engineering_context,
            context_budget=budget.token_limit,
        )

        print("=" * 80)
        print("PROMPT STATISTICS")
        print("=" * 80)

        total = 0

        for i, m in enumerate(messages, 1):
            size = len(m.content.encode("utf-8"))
            total += size
            print(f"Message {i}: {size:,} bytes")

        print("-" * 80)
        print(f"TOTAL: {total:,} bytes")
        print(f"BUDGET: {budget.byte_limit:,} bytes")
        print("=" * 80)

        execution = ExecutionRequest(
            
            messages=messages,
        )

        return engine.execute(execution)


generator = CodeGenerator()
