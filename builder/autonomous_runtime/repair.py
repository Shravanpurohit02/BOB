from __future__ import annotations

from builder.autopatch import engine as autopatch


class RepairEngine:

    def repair(
        self,
        workspace: str,
        paths: list[str] | None = None,
        context: dict | None = None,
    ):

        context = dict(context or {})

        learned_context = context.get(
            "learned_context",
            [],
        )

        if not isinstance(
            learned_context,
            list,
        ):
            learned_context = []

        context["learned_context"] = [
            dict(item)
            for item in learned_context
            if isinstance(item, dict)
        ]

        context["knowledge_count"] = len(
            context["learned_context"]
        )

        if not paths:
            try:
                return autopatch.patch(
                    workspace=workspace,
                    context=context,
                )

            except TypeError:
                return autopatch.patch(
                    workspace
                )

            except Exception:
                return {
                    "success": False,
                    "patched": 0,
                }

        results = []

        for path in paths:
            local_context = dict(context)

            local_context["filename"] = path
            local_context["target_file"] = path

            try:
                results.append(
                    autopatch.patch(
                        workspace=workspace,
                        filename=path,
                        objective=local_context.get(
                            "objective",
                            "Automatic repair",
                        ),
                        context=local_context,
                    )
                )

            except Exception as exc:
                results.append(
                    {
                        "success": False,
                        "target": path,
                        "reason": str(exc),
                    }
                )

        return {
            "success": bool(results)
            and all(
                r.get("success", False)
                for r in results
            ),
            "patched": sum(
                1
                for r in results
                if r.get("success")
            ),
            "results": results,
            "knowledge_count": len(
                context["learned_context"]
            ),
        }


repair = RepairEngine()
