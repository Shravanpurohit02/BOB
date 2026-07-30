from dataclasses import dataclass, field




from time import perf_counter


@dataclass(slots=True)
class RepositoryScope:

    files: list[str] = field(
        default_factory=list,
    )

    modules: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class ExecutionAnalytics:

    tasks: int = 0

    completed: int = 0

    failed: int = 0

    retries: int = 0

    duration: float = 0.0

    decisions: list[str] = field(
        default_factory=list,
    )

    repository: RepositoryScope = field(
        default_factory=RepositoryScope,
    )


@dataclass(slots=True)
class ExecutionResult:
    total: int = 0
    completed: int = 0
    failed: int = 0
    executed: list[str] = field(default_factory=list)

    analytics: ExecutionAnalytics = field(
        default_factory=ExecutionAnalytics,
    )


class PlanExecutor:










    def _repository_scope(
        self,
        plan,
    ):

        scope = {
            "files": set(),
            "modules": set(),
        }

        for milestone in plan.milestones:
            for job in milestone.jobs:
                for task in job.tasks:

                    scope["files"].add(
                        task.title
                    )

                    scope["modules"].add(
                        task.title.split(
                            "/"
                        )[0]
                    )

        repository = RepositoryScope()

        repository.files.extend(
            sorted(scope["files"])
        )

        repository.modules.extend(
            sorted(scope["modules"])
        )

        return repository

    def _coordinate_agents(
        self,
        tasks,
    ):

        assignments = {}

        agents = (
            "planner",
            "engineer",
            "reviewer",
            "validator",
        )

        for index, task in enumerate(tasks):

            agent = agents[
                index % len(agents)
            ]

            task.metadata["agent"] = agent

            assignments[
                task.id
            ] = agent

        return assignments

    def _evolve_task(
        self,
        task,
    ):

        metadata = getattr(
            task,
            "metadata",
            {},
        )

        metadata.setdefault(
            "evolution",
            []
        )

        metadata["evolution"].append(
            {
                "status": task.status,
                "retries": getattr(
                    task,
                    "retries",
                    0,
                ),
            }
        )

        task.metadata = metadata

        return task

    def _decision(
        self,
        task,
    ):

        if getattr(
            task,
            "dependencies",
            [],
        ):
            return "dependency"

        if getattr(
            task,
            "priority",
            100,
        ) <= 10:
            return "priority"

        return "standard"

    def _execute_task(
        self,
        task,
        action,
    ):

        import time

        while True:

            try:

                action(task)

                task.status = "completed"

                return True

            except Exception as exc:

                task.retries += 1

                classification = self._classify_failure(
                    exc,
                )

                task.metadata["failure"] = classification

                if (
                    classification == "permanent"
                    or self._retry_budget(task) == 0
                ):
                    task.status = "failed"
                    return False

                delay = min(
                    2 ** task.retries,
                    8,
                )

                task.metadata["backoff"] = delay

                time.sleep(delay)


    TRANSIENT_ERRORS = {
        "TimeoutError",
        "ConnectionError",
        "OSError",
    }

    def _classify_failure(
        self,
        exc,
    ):

        name = type(exc).__name__

        if name in self.TRANSIENT_ERRORS:
            return "transient"

        return "permanent"


    def _retry_budget(
        self,
        task,
    ):

        retries = getattr(
            task,
            "retries",
            0,
        )

        return max(
            0,
            3 - retries,
        )


    def _dependency_order(
        self,
        tasks,
    ):

        ordered = []
        completed = set()
        pending = list(tasks)

        while pending:

            progress = False

            for task in pending[:]:

                deps = set(
                    getattr(
                        task,
                        "dependencies",
                        [],
                    )
                )

                if deps <= completed:

                    ordered.append(task)

                    completed.add(task.id)

                    pending.remove(task)

                    progress = True

            if not progress:

                ordered.extend(
                    sorted(
                        pending,
                        key=lambda t: t.title,
                    )
                )

                break

        return ordered


    def execute(
        self,
        plan,
        transaction=None,
    ):

        started = perf_counter()

        result = ExecutionResult()

        result.analytics.repository = (
            self._repository_scope(
                plan,
            )
        )
        if (
            transaction is not None
            and getattr(transaction, "transaction", None) is not None
        ):
            try:
                plan.metadata["transaction"] = transaction.id
            except Exception:
                pass

        for milestone in plan.milestones:
            for job in milestone.jobs:

                tasks = self._dependency_order(
                    sorted(
                        job.tasks,
                        key=lambda t: (
                            getattr(
                                t,
                                "priority",
                                100,
                            ),
                            t.title,
                        ),
                    )
                )

                self._coordinate_agents(
                    tasks,
                )

                for task in tasks:

                    if getattr(
                        task,
                        "dependencies",
                        [],
                    ):
                        task.metadata["dependency_count"] = len(
                            task.dependencies
                        )

                    task.status = "completed"

                    self._evolve_task(
                        task,
                    )

                    decision = self._decision(
                        task,
                    )

                    result.analytics.decisions.append(
                        decision + ":" + task.title
                    )

                    result.total += 1
                    result.completed += 1
                    result.executed.append(task.title)

                    result.analytics.tasks += 1
                    result.analytics.completed += 1
                    result.analytics.retries += getattr(
                        task,
                        "retries",
                        0,
                    )

        result.analytics.duration = round(
            perf_counter() - started,
            6,
        )

        return result


executor = PlanExecutor()
