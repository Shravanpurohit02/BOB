from dataclasses import dataclass, field

from .change_executor import change_executor


@dataclass(slots=True)
class ChangeResult:
    order: int
    file: str
    status: str
    message: str = ""


@dataclass(slots=True)
class ChangeEngineResult:
    query: str
    risk: str
    completed: list[ChangeResult] = field(default_factory=list)


class ChangeEngine:
    def build(self, workspace: str):
        change_executor.build(workspace)


    def execute(
        self,
        query: str,
        *,
        transaction=None,
    ):

        plan = change_executor.create_plan(query)

        report = change_executor.execute(
            plan,
            transaction=transaction,
        )

        result = ChangeEngineResult(
            query=query,
            risk=plan.risk,
        )

        for operation in report.operations:
            result.completed.append(
                ChangeResult(
                    order=operation.order,
                    file=operation.file,
                    status=operation.status.value,
                    message=operation.message,
                )
            )

        return result
change_engine = ChangeEngine()
