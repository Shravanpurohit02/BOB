from builder.autonomous.task import AutonomousTask


class Planner:

    DEFAULT_PHASES = [
        "planning",
        "execution",
        "validation",
        "testing",
        "repair",
        "completion",
    ]

    def create(
        self,
        objective: str,
    ):

        task = AutonomousTask(
            objective=objective,
        )

        task.phases.extend(
            self.DEFAULT_PHASES
        )

        return task


planner = Planner()
