from builder.autopatch import engine as autopatch


class RepairEngine:

    def repair(
        self,
        workspace: str,
        paths: list[str] | None = None,
        context: dict | None = None,
    ):

        context = context or {}

        # ------------------------------------------------------------------
        # Backward-compatible single repair
        # ------------------------------------------------------------------

        if not paths:

            try:
                return autopatch.patch(
                    workspace=workspace,
                    context=context,
                )

            except TypeError:
                return autopatch.patch(workspace)

            except Exception:
                return {
                    "success": False,
                    "patched": 0,
                }

        # ------------------------------------------------------------------
        # Selective repair
        # ------------------------------------------------------------------

        results = []

        for path in paths:

            try:

                results.append(
                    autopatch.patch(
                        workspace=workspace,
                        filename=path,
                        context=context,
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
            "success": all(
                r.get("success", False)
                for r in results
            ),
            "patched": sum(
                1
                for r in results
                if r.get("success")
            ),
            "results": results,
        }


repair = RepairEngine()
