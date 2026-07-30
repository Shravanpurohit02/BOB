from builder.autopatch.applier import applier
from builder.autopatch.generator import generator
from builder.autopatch.resolver import resolver


class AutoPatch:

    def patch(
        self,
        workspace,
        filename=None,
        objective=None,
        context=None,
    ):

        context = context or {}

        filename = (
            filename
            or context.get("filename")
            or context.get("target_file")
        )

        objective = (
            objective
            or context.get("objective")
            or "Automatic repair"
        )

        if not filename:
            return {
                "success": False,
                "reason": "No target file supplied.",
            }

        target = resolver.find(
            workspace,
            filename,
        )

        if not target:
            return {
                "success": False,
                "reason": "Target file not found.",
            }

        result = generator.generate(
            workspace,
            target,
            objective,
        )

        applier.apply(
            target,
            result.code,
        )

        return {
            "success": True,
            "target": target,
        }


engine = AutoPatch()
