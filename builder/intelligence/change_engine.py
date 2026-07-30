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

    def execute(self, query: str):

        plan = change_executor.create_plan(query)

        result = ChangeEngineResult(
            query=query,
            risk=plan.risk,
        )

        for operation in plan.operations:
            result.completed.append(
                ChangeResult(
                    order=operation.order,
                    file=operation.file,
                    status=operation.status,
                    message="Ready for edit" if operation.status == "ready" else "Missing file",
                )
            )

        return result


change_engine = ChangeEngine()
