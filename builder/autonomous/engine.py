from builder.autonomous.controller import controller

class AutonomousEngine:

    def execute(
        self,
        objective: str,
        **context,
    ):
        return controller.run(
            objective,
            **context,
        )

engine = AutonomousEngine()
