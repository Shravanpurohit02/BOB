from builder.autonomous.executor import executor
from builder.autonomous.planner import planner


class Controller:

    MAX_ATTEMPTS = 3

    def run(
        self,
        objective: str,
        **context,
    ):

        task = planner.create(objective)

        task.context.update(context)

        task.context["history"] = []

        attempt = 0

        result = None

        while attempt < self.MAX_ATTEMPTS:

            attempt += 1

            task.context["attempt"] = attempt

            result = executor.execute(task)

            task.context["history"].append(
                {
                    "attempt": attempt,
                    "success": result.success,
                    "message": result.message,
                }
            )

            if result.success:
                task.status = "completed"
                break

        if not result.success:
            task.status = "failed"

        return task, result


controller = Controller()
