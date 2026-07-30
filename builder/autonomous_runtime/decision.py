class DecisionEngine:

    def decide(self, runtime):

        validation = runtime.context.pipeline.context.validation

        if validation["failed"] == 0:
            return "complete"

        return "repair"


decision = DecisionEngine()
