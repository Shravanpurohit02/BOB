class MultiFileCodeGenerator:

    def generate(
        self,
        strategy,
    ):

        outputs = []

        for action in strategy["actions"]:

            outputs.append(
                {
                    "file": action["file"],
                    "mode": action["mode"],
                    "generated": True,
                    "patch": self._patch(
                        action,
                    ),
                }
            )

        return outputs

    def _patch(
        self,
        action,
    ):

        return {
            "action": action["action"],
            "mode": action["mode"],
        }

    def summary(
        self,
        outputs,
    ):

        return {
            "files": len(outputs),
            "generated": sum(
                item["generated"]
                for item in outputs
            ),
        }


generator = MultiFileCodeGenerator()
