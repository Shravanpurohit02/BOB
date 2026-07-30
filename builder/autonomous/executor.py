from builder.execution.context import ExecutionContext
from builder.execution.executor import executor as execution


class Executor:

    def execute(self, task):

        context = ExecutionContext()

        context.job_id = task.id

        task.status = "running"

        for phase in task.phases:

            if phase not in task.completed:
                task.completed.append(phase)

            if phase == "execution":

                result = execution.execute(context)

                task.context["execution"] = result

                if not result.success:
                    task.status = "failed"
                    return result

        task.status = "completed"

        return task.context["execution"]


executor = Executor()
