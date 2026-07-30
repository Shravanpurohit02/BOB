from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeMetrics:

    attempts: int = 0
    completed: int = 0
    failed: int = 0
    stages: int = 0


class MetricsEngine:

    def collect(self, runtime):

        return RuntimeMetrics(
            attempts=runtime.context.attempts,
            completed=int(runtime.completed),
            failed=int(not runtime.success),
            stages=len(runtime.history),
        )


metrics = MetricsEngine()
