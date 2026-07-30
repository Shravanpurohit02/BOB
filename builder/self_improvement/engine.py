import time

from builder.self_improvement.analyzer import analyzer
from builder.self_improvement.planner import planner


class SelfImprovementResult:

    __slots__ = (
        "success",
        "elapsed",
        "issues",
        "improvements",
        "review_tasks",
    )

    def __init__(self):
        self.success = False
        self.elapsed = 0.0
        self.issues = []
        self.improvements = []
        self.review_tasks = []


class SelfImprovementEngine:

    def inspect(
        self,
        workspace: str,
    ):

        issues = analyzer.analyze(workspace)

        return planner.build(issues)

    def improve(
        self,
        workspace: str,
    ):

        # Lazy import to avoid circular dependency with builder.review
        from builder.review.engine import (
            engine as review_engine,
        )

        started = time.perf_counter()

        result = SelfImprovementResult()

        issues = analyzer.analyze(workspace)

        improvements = planner.build(issues)

        result.issues = issues
        result.improvements = improvements

        for improvement in improvements:

            task = review_engine.submit(
                improvement
            )

            result.review_tasks.append(
                task
            )

        result.success = True

        result.elapsed = round(
            time.perf_counter() - started,
            6,
        )

        return result


engine = SelfImprovementEngine()
