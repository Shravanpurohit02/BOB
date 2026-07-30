class AutonomousTaskDecomposer:

    PHASES = (
        "analysis",
        "planning",
        "implementation",
        "validation",
        "integration",
        "regression",
    )

    def decompose(
        self,
        task,
    ):

        subtasks = []

        priority = task.get(
            "priority",
            "normal",
        )

        for order, phase in enumerate(
            self.PHASES,
            start=1,
        ):

            subtasks.append(
                {
                    "id": order,
                    "phase": phase,
                    "title": f"{phase}: {task['title']}",
                    "priority": priority,
                    "completed": False,
                }
            )

        return subtasks

    def summary(
        self,
        subtasks,
    ):

        return {
            "total": len(subtasks),
            "completed": sum(
                task["completed"]
                for task in subtasks
            ),
            "remaining": sum(
                not task["completed"]
                for task in subtasks
            ),
        }


engine = AutonomousTaskDecomposer()
