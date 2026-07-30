from pathlib import Path
import subprocess
import sys

from builder.patch import engine as patch
from builder.review import engine as review
from builder.pipeline import engine as pipeline
from builder.execution.context import ExecutionContext
from builder.execution.executor import executor
from builder.autonomous_runtime import engine as runtime_engine
from builder.engineering.transaction.engine import engine as transactions
from builder.regression.models import RegressionResult
from builder.regression.test_execution_snapshot import (
    run as snapshot_test,
)


class RegressionEngine:

    EXPECTED_PIPELINE = [
        "changeset",
        "output",
        "semantic",
        "planning",
        "impact",
        "validation",
        "testing",
        "finalization",
    ]

    def run(self):

        result = RegressionResult()

        self._patch_suite(result)
        self._review_suite(result)
        self._output_suite(result)
        self._pipeline_suite(result)
        self._cli_suite(result)
        self._execution_suite(result)
        self._runtime_suite(result)
        self._transaction_suite(result)
        self._resume_suite(result)
        self._snapshot_suite(result)
        self._recovery_stress_suite(result)
        self._orchestrator_suite(result)
        self._parallel_scheduler_suite(result)
        self._worker_pool_suite(result)
        self._resource_manager_suite(result)
        self._worker_recovery_suite(result)
        self._planning_intelligence_suite(result)
        self._dependency_graph_suite(result)
        self._failure_classification_suite(result)
        self._self_healing_execution_suite(result)
        self._execution_analytics_suite(result)
        self._decision_engine_suite(result)
        self._autonomous_code_evolution_suite(result)
        self._multi_agent_coordination_suite(result)
        self._repository_engineering_suite(result)
        self._end_to_end_builder_suite(result)
        self._provider_runtime_suite(result)
        self._provider_execution_suite(result)
        self._context_intelligence_suite(result)
        self._semantic_repository_suite(result)
        self._repository_intelligence_suite(result)
        self._autonomous_engineering_suite(result)
        self._autonomous_code_generation_suite(result)
        self._autonomous_review_suite(result)
        self._autonomous_testing_suite(result)

        return result

    def _record(self, result, name, passed):
        result.total += 1
        if passed:
            result.passed += 1
            result.tests.append(f"{name}: PASS")
        else:
            result.failed += 1
            result.tests.append(f"{name}: FAIL")

    def _patch_suite(self, result):

        tmp = Path(".builder/temp/regression_patch_test.py")
        tmp.parent.mkdir(parents=True, exist_ok=True)

        original = "def value():\n    return 1\n"
        updated = "def value():\n    return 2\n"

        tmp.write_text(original, encoding="utf-8")

        try:
            p = patch.create(str(tmp), updated)

            ok = patch.validate(p) and patch.compile(p)

            if ok:
                patch.commit(p)
                ok = tmp.read_text(encoding="utf-8") == updated

                patch.rollback(p)
                ok = ok and (
                    tmp.read_text(encoding="utf-8") == original
                )

            self._record(result, "Patch", ok)

        except Exception:
            self._record(result, "Patch", False)

        finally:
            tmp.unlink(missing_ok=True)

    def _review_suite(self, result):

        try:
            tasks = review.list()

            if not tasks:
                self._record(result, "Review", False)
                return

            task = tasks[0]

            review.approve(
                task.id,
                reviewer="regression",
            )

            refreshed = review.list()[0]

            ok = (
                refreshed.status == "approved"
                and refreshed.reviewer == "regression"
            )

            self._record(result, "Review", ok)

        except Exception:
            self._record(result, "Review", False)

    def _output_suite(self, result):

        try:

            output = Path(".builder/output")

            ok = any(
                (d / "metadata.json").exists()
                and (d / "objective.md").exists()
                for d in output.iterdir()
                if d.is_dir()
            )

            self._record(result, "Output", ok)

        except Exception:

            self._record(result, "Output", False)

    def _pipeline_suite(self, result):

        try:

            r = pipeline.start(
                "Regression Pipeline Test",
                str(Path.cwd()),
            )

            stages = r.stages

            ok = (
                stages == self.EXPECTED_PIPELINE
                and len(stages) == len(set(stages))
            )

            self._record(result, "Pipeline", ok)

        except Exception:

            self._record(result, "Pipeline", False)




    def _cli_suite(self, result):

        try:

            cmd = [
                sys.executable,
                "-m",
                "builder",
                "status",
            ]

            proc = subprocess.run(
                cmd,
                env={
                    "PYTHONPATH": ".builder",
                    **__import__("os").environ,
                },
                capture_output=True,
                text=True,
            )

            ok = (
                proc.returncode == 0
                and "VIDHI BUILDER STATUS" in proc.stdout
            )

            self._record(result, "CLI", ok)

        except Exception:

            self._record(result, "CLI", False)




    def _execution_suite(self, result):

        try:

            ctx = ExecutionContext(
                plan_id="regression-plan",
                worker_id="regression-worker",
                job_id="regression-job",
            )

            execution = executor.execute(ctx)

            ok = (
                execution.success is True
                and execution.message == "completed"
                and len(execution.failed_stages) == 0
                and execution.validation.get("failed", 0) == 0
                and execution.testing.get("failed", 0) == 0
                and len(execution.artifacts) > 0
                and bool(execution.changeset)
                and ctx.plan_id == "regression-plan"
                and ctx.worker_id == "regression-worker"
                and ctx.job_id == "regression-job"
            )

            self._record(result, "Execution", ok)

        except Exception:

            self._record(result, "Execution", False)




    def _runtime_suite(self, result):

        try:

            runtime = runtime_engine.execute(
                "Runtime Regression",
                ".",
            )

            ok = (
                runtime.success is True
                and runtime.completed is True
                and runtime.context.attempts >= 1
                and len(runtime.history) > 0
                and runtime.context.metadata.get("events", 0) > 0
                and bool(runtime.context.metadata.get("metrics"))
            )

            self._record(
                result,
                "Autonomous Runtime",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Autonomous Runtime",
                False,
            )


    def _transaction_suite(self, result):

        try:

            tmp = Path(".builder/temp/transaction_test.txt")
            tmp.parent.mkdir(parents=True, exist_ok=True)

            original = "original"
            updated = "modified"

            tmp.write_text(original, encoding="utf-8")

            tx = transactions.begin(
                objective="Regression",
                workspace=".",
            )

            transactions.snapshot_file(
                tx,
                str(tmp),
            )

            tmp.write_text(updated, encoding="utf-8")

            transactions.rollback(
                tx,
            )

            ok = (
                tmp.read_text(encoding="utf-8")
                == original
            )

            self._record(
                result,
                "Transaction",
                ok,
            )

            tmp.unlink(missing_ok=True)

        except Exception:

            self._record(
                result,
                "Transaction",
                False,
            )



    def _snapshot_suite(
        self,
        result,
    ):

        try:

            self._record(
                result,
                "Execution Snapshot",
                snapshot_test(),
            )

        except Exception:

            self._record(
                result,
                "Execution Snapshot",
                False,
            )



    def _resume_suite(self, result):

        try:

            from builder.execution.snapshot.recovery import (
                recovery,
            )
            from builder.execution.snapshot.models import (
                ExecutionSnapshot,
                ExecutionCheckpoint,
            )

            snapshot = ExecutionSnapshot()

            snapshot.checkpoints = [
                ExecutionCheckpoint(
                    stage="changeset",
                    status="completed",
                ),
                ExecutionCheckpoint(
                    stage="output",
                    status="completed",
                ),
            ]

            stage = recovery.next_stage(
                snapshot,
                [
                    "changeset",
                    "output",
                    "planning",
                    "validation",
                    "testing",
                ],
            )

            self._record(
                result,
                "Execution Resume",
                stage == "planning",
            )

        except Exception:

            self._record(
                result,
                "Execution Resume",
                False,
            )


    def _recovery_stress_suite(self, result):

        try:

            from builder.execution.snapshot.models import (
                ExecutionSnapshot,
            )

            from builder.execution.snapshot.recovery import (
                recovery,
            )

            snapshots = []

            for i in range(100):

                s = ExecutionSnapshot()

                s.status = (
                    "completed"
                    if i % 2
                    else "running"
                )

                snapshots.append(s)

            active = [
                s
                for s in snapshots
                if s.status in recovery.ACTIVE
            ]

            ok = len(active) == 50

            self._record(
                result,
                "Recovery Stress",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Recovery Stress",
                False,
            )


    def _orchestrator_suite(self, result):

        try:

            from builder.execution.scheduler import scheduler

            Job = type(
                "Job",
                (),
                {},
            )

            jobs = []

            for priority in (3, 1, 2):

                job = Job()

                job.id = str(priority)
                job.status = "pending"
                job.priority = priority
                job.dependencies = []

                jobs.append(job)

            ordered = scheduler.schedule(jobs)

            ok = [
                j.priority
                for j in ordered
            ] == [1, 2, 3]

            self._record(
                result,
                "Orchestrator",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Orchestrator",
                False,
            )


    def _parallel_scheduler_suite(self, result):

        try:

            from builder.execution.scheduler import scheduler

            Job = type("Job", (), {})

            jobs = []

            for i in range(10):

                job = Job()

                job.id = str(i)
                job.status = "pending"
                job.priority = i
                job.dependencies = []

                jobs.append(job)

            batches = scheduler.schedule_parallel(
                jobs,
                workers=3,
            )

            flattened = [
                j.id
                for batch in batches
                for j in batch
            ]

            ok = (
                len(batches) == 4
                and len(flattened) == 10
                and flattened == sorted(flattened)
            )

            self._record(
                result,
                "Parallel Scheduler",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Parallel Scheduler",
                False,
            )


    def _worker_pool_suite(self, result):

        try:

            from builder.execution.scheduler import worker_pool

            worker = worker_pool.acquire()

            ok = (
                worker is not None
                and worker["status"] == "busy"
            )

            if worker is not None:
                worker_pool.release(worker["id"])

                ok = ok and (
                    worker["status"] == "idle"
                )

            self._record(
                result,
                "Worker Pool",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Worker Pool",
                False,
            )


    def _resource_manager_suite(self, result):

        try:

            from builder.execution.scheduler import worker_pool

            worker_pool.scale(6)

            metrics = worker_pool.health()

            ok = (
                metrics["workers"] == 6
                and metrics["healthy"] == 6
                and metrics["busy"] == 0
                and metrics["idle"] == 6
            )

            worker_pool.scale(4)

            self._record(
                result,
                "Resource Manager",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Resource Manager",
                False,
            )


    def _worker_recovery_suite(self, result):

        try:

            from builder.execution.scheduler import worker_pool

            worker_pool.scale(4)

            worker = worker_pool.workers[0]

            worker["status"] = "failed"

            recovered = worker_pool.recover_workers()

            metrics = worker_pool.metrics()

            ok = (
                recovered == 1
                and worker["status"] == "idle"
                and metrics["healthy"] == 4
                and metrics["workers"] == 4
            )

            self._record(
                result,
                "Worker Recovery",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Worker Recovery",
                False,
            )


    def _planning_intelligence_suite(self, result):

        try:

            from builder.planning.models import (
                EngineeringPlan,
                Milestone,
                Job,
                Task,
            )

            from builder.planning.executor import executor

            plan = EngineeringPlan()

            milestone = Milestone()

            job = Job()

            low = Task(
                title="low",
                priority=50,
            )

            high = Task(
                title="high",
                priority=1,
            )

            job.tasks.extend(
                [
                    low,
                    high,
                ]
            )

            milestone.jobs.append(job)

            plan.milestones.append(
                milestone
            )

            execution = executor.execute(plan)

            ok = (
                execution.executed
                == ["high", "low"]
            )

            self._record(
                result,
                "Planning Intelligence",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Planning Intelligence",
                False,
            )


    def _dependency_graph_suite(self, result):

        try:

            from builder.planning.models import (
                EngineeringPlan,
                Milestone,
                Job,
                Task,
            )

            from builder.planning.executor import executor

            plan = EngineeringPlan()

            milestone = Milestone()

            job = Job()

            first = Task(
                title="first",
                priority=1,
            )

            second = Task(
                title="second",
                priority=2,
                dependencies=[first.id],
            )

            third = Task(
                title="third",
                priority=3,
                dependencies=[second.id],
            )

            job.tasks.extend(
                [
                    third,
                    second,
                    first,
                ]
            )

            milestone.jobs.append(job)

            plan.milestones.append(
                milestone
            )

            execution = executor.execute(plan)

            ok = (
                execution.executed
                == [
                    "first",
                    "second",
                    "third",
                ]
            )

            self._record(
                result,
                "Dependency Graph",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Dependency Graph",
                False,
            )


    def _failure_classification_suite(self, result):

        try:

            from builder.planning.executor import executor
            from builder.planning.models import Task

            transient = executor._classify_failure(
                TimeoutError()
            )

            permanent = executor._classify_failure(
                ValueError()
            )

            task = Task()

            task.retries = 1

            budget = executor._retry_budget(
                task
            )

            ok = (
                transient == "transient"
                and permanent == "permanent"
                and budget == 2
            )

            self._record(
                result,
                "Failure Classification",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Failure Classification",
                False,
            )


    def _self_healing_execution_suite(self, result):

        try:

            from builder.planning.executor import executor
            from builder.planning.models import Task

            task = Task()

            attempts = {"count": 0}

            def action(_):

                attempts["count"] += 1

                if attempts["count"] < 3:
                    raise TimeoutError()

            ok = executor._execute_task(
                task,
                action,
            )

            passed = (
                ok
                and task.status == "completed"
                and task.retries == 2
                and task.metadata.get("failure") == "transient"
                and task.metadata.get("backoff") == 4
            )

            self._record(
                result,
                "Self-Healing Execution",
                passed,
            )

        except Exception:

            self._record(
                result,
                "Self-Healing Execution",
                False,
            )


    def _execution_analytics_suite(self, result):

        try:

            from builder.planning.models import (
                EngineeringPlan,
                Milestone,
                Job,
                Task,
            )

            from builder.planning.executor import executor

            plan = EngineeringPlan()

            milestone = Milestone()

            job = Job()

            job.tasks.append(
                Task(title="analytics")
            )

            milestone.jobs.append(job)
            plan.milestones.append(milestone)

            execution = executor.execute(plan)

            ok = (
                execution.analytics.tasks == 1
                and execution.analytics.completed == 1
                and len(execution.analytics.decisions) == 1
            )

            self._record(
                result,
                "Execution Analytics",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Execution Analytics",
                False,
            )


    def _decision_engine_suite(self, result):

        try:

            from builder.planning.executor import executor
            from builder.planning.models import Task

            standard = Task(
                title="standard",
            )

            priority = Task(
                title="priority",
                priority=1,
            )

            dependency = Task(
                title="dependency",
                dependencies=["abc"],
            )

            ok = (
                executor._decision(standard) == "standard"
                and executor._decision(priority) == "priority"
                and executor._decision(dependency) == "dependency"
            )

            self._record(
                result,
                "Decision Engine",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Decision Engine",
                False,
            )


    def _autonomous_code_evolution_suite(self, result):

        try:

            from builder.planning.executor import executor
            from builder.planning.models import Task

            task = Task(
                title="evolve",
            )

            task.status = "completed"

            executor._evolve_task(task)

            evolution = task.metadata.get(
                "evolution",
                [],
            )

            ok = (
                len(evolution) == 1
                and evolution[0]["status"] == "completed"
                and evolution[0]["retries"] == 0
            )

            self._record(
                result,
                "Autonomous Code Evolution",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Autonomous Code Evolution",
                False,
            )


    def _multi_agent_coordination_suite(self, result):

        try:

            from builder.planning.executor import executor
            from builder.planning.models import Task

            tasks = [
                Task(title="planner"),
                Task(title="engineer"),
                Task(title="reviewer"),
                Task(title="validator"),
            ]

            assignments = executor._coordinate_agents(tasks)

            expected = [
                "planner",
                "engineer",
                "reviewer",
                "validator",
            ]

            ok = (
                len(assignments) == 4
                and [
                    t.metadata.get("agent")
                    for t in tasks
                ] == expected
            )

            self._record(
                result,
                "Multi-Agent Coordination",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Multi-Agent Coordination",
                False,
            )


    def _repository_engineering_suite(self, result):

        try:

            from builder.planning.models import (
                EngineeringPlan,
                Milestone,
                Job,
                Task,
            )

            from builder.planning.executor import executor

            plan = EngineeringPlan()

            milestone = Milestone()

            job = Job()

            job.tasks.append(
                Task(title="builder/core/jobs.py")
            )

            job.tasks.append(
                Task(title="builder/planning/executor.py")
            )

            milestone.jobs.append(job)
            plan.milestones.append(milestone)

            execution = executor.execute(plan)

            repository = execution.analytics.repository

            ok = (
                len(repository.files) == 2
                and "builder" in repository.modules
            )

            self._record(
                result,
                "Repository Engineering",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Repository Engineering",
                False,
            )


    def _end_to_end_builder_suite(self, result):

        try:

            from builder.planning.models import (
                EngineeringPlan,
                Milestone,
                Job,
                Task,
            )

            from builder.planning.executor import executor

            plan = EngineeringPlan()

            milestone = Milestone(
                title="End-to-End"
            )

            job = Job(
                title="Builder"
            )

            job.tasks.extend([
                Task(
                    title="planner.py",
                    priority=1,
                ),
                Task(
                    title="executor.py",
                    priority=2,
                ),
                Task(
                    title="validator.py",
                    priority=3,
                ),
            ])

            milestone.jobs.append(job)
            plan.milestones.append(milestone)

            execution = executor.execute(plan)

            ok = (
                execution.completed == 3
                and execution.failed == 0
                and execution.total == 3
                and len(execution.executed) == 3
                and execution.analytics.tasks == 3
                and execution.analytics.completed == 3
                and len(execution.analytics.repository.files) == 3
            )

            self._record(
                result,
                "End-to-End Builder",
                ok,
            )

        except Exception:

            self._record(
                result,
                "End-to-End Builder",
                False,
            )


    def _provider_runtime_suite(self, result):

        try:

            from builder.providers.runtime.loader import loader
            from builder.providers.runtime.router import router

            registry = loader.load()

            providers = registry.all()

            ok = (
                len(providers) > 0
                and registry.get("groq") is not None
                and isinstance(registry.enabled(), list)
                and isinstance(registry.free(), list)
                and isinstance(registry.supports("streaming"), list)
                and router.available() == registry.enabled()
            )

            best = router.default()

            if registry.enabled():
                ok = ok and (best is not None)

            self._record(
                result,
                "Provider Runtime",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Provider Runtime",
                False,
            )


    def _provider_execution_suite(self, result):

        try:

            from builder.providers.execution.payloads import builder as payload_builder
            from builder.providers.execution.endpoints import router as endpoint_router
            from builder.providers.execution.normalizer import normalizer
            from builder.providers.execution.failover import engine as failover
            from builder.providers.execution.streaming import engine as streaming
            from builder.providers.chat.messages import Message

            class Provider:

                def __init__(self, api_type):

                    self.api_type = api_type
                    self.model = "demo-model"
                    self.supports_streaming = True

            class Request:

                model = ""
                temperature = 0.2
                max_tokens = 128
                stream = True

                messages = [
                    Message(
                        role="user",
                        content="hello",
                    )
                ]

            request = Request()

            openai = payload_builder.build(
                Provider("openai"),
                request,
            )

            anthropic = payload_builder.build(
                Provider("anthropic"),
                request,
            )

            gemini = payload_builder.build(
                Provider("gemini"),
                request,
            )

            endpoint = endpoint_router.endpoint(
                Provider("openai"),
                "demo-model",
            )

            class Response:

                is_success = True
                status_code = 200
                text = "hello"

                def json(self):

                    return {
                        "choices":[
                            {
                                "message":{
                                    "content":"hello"
                                }
                            }
                        ],
                        "usage":{},
                    }

            normalized = normalizer.normalize(
                Provider("openai"),
                Response(),
            )

            ok = (
                "messages" in openai
                and "messages" in anthropic
                and anthropic["messages"][0]["role"] == "user"
                and "contents" in gemini
                and endpoint == "/chat/completions"
                and normalized["text"] == "hello"
                and streaming.enabled(
                    Provider("openai"),
                    request,
                )
                and failover.should_retry(
                    type(
                        "Retry",
                        (),
                        {
                            "is_success":False,
                            "status_code":429,
                        },
                    )()
                )
            )

            self._record(
                result,
                "Provider Execution",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Provider Execution",
                False,
            )


    def _context_intelligence_suite(self, result):

        try:

            from builder.context.token_budget import manager
            from builder.context.compression import compressor
            from builder.context.provider_optimizer import optimizer
            from builder.context.cache import cache

            class Provider:
                name = "openai"

            prompt = "Implement dependency graph"

            files = [
                {
                    "path":"demo.py",
                    "lines":100,
                    "source":"print('x')\n"*100,
                }
            ]

            budget = manager.budget(
                Provider(),
            )

            estimate = manager.estimate(
                prompt,
            )

            compressed = compressor.compress_files(
                files,
                500,
            )

            optimized = optimizer.optimize(
                Provider(),
                prompt,
                files,
            )

            cache.put(
                "/repo",
                prompt,
                optimized,
            )

            cached = cache.get(
                "/repo",
                prompt,
            )

            ok = (
                budget == 128000
                and estimate > 0
                and len(compressed) == 1
                and optimized["budget"] == 128000
                and cached is not None
                and cached["value"]["budget"] == 128000
            )

            cache.invalidate(
                "/repo",
                prompt,
            )

            self._record(
                result,
                "Context Intelligence",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Context Intelligence",
                False,
            )


    def _semantic_repository_suite(self, result):

        try:

            from builder.context.repository_index import index
            from builder.context.semantic_search import engine as semantic
            from builder.context.hybrid_retrieval import engine as hybrid
            from builder.ast.module import Module

            repo = index.build(".")

            router = Module(
                path="providers/runtime/router.py",
            )
            router.classes.append(
                "ProviderRouter",
            )

            loader = Module(
                path="providers/runtime/loader.py",
            )
            loader.classes.append(
                "ProviderLoader",
            )

            graph = {
                "reverse":{
                    "providers/runtime/router.py":["a","b"],
                    "providers/runtime/loader.py":["a"],
                },
                "depth":{
                    "providers/runtime/router.py":3,
                    "providers/runtime/loader.py":1,
                },
            }

            semantic_results = semantic.search(
                [router, loader],
                "provider router",
            )

            hybrid_results = hybrid.retrieve(
                [router, loader],
                graph,
                "provider router",
            )

            ok = (
                len(repo["python"]) > 0
                and len(semantic_results) >= 1
                and semantic_results[0].path == "providers/runtime/router.py"
                and len(hybrid_results) >= 1
                and hybrid_results[0].path == "providers/runtime/router.py"
            )

            self._record(
                result,
                "Semantic Repository",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Semantic Repository",
                False,
            )


    def _repository_intelligence_suite(self, result):

        try:

            from builder.context.repository_graph import engine as repository_graph
            from builder.context.cross_reference import engine as cross_reference
            from builder.context.architecture import engine as architecture
            from builder.context.change_impact import engine as impact
            from builder.context.repository_memory import memory
            from builder.context.file_planner import planner
            from builder.ast.module import Module

            a = Module(path="core.py")
            b = Module(path="service.py")
            c = Module(path="api.py")

            imports = {
                "imports":{
                    "core.py":[],
                    "service.py":["core.py"],
                    "api.py":["service.py"],
                },
                "reverse":{
                    "core.py":["service.py"],
                    "service.py":["api.py"],
                    "api.py":[],
                },
            }

            symbols = {
                "exports":{
                    "core.py":["Core"],
                    "service.py":["Service"],
                    "api.py":["API"],
                },
                "references":{
                    "core.py":[],
                    "service.py":["Core"],
                    "api.py":["Service"],
                },
                "definitions":{
                    "Core":["core.py"],
                    "Service":["service.py"],
                },
            }

            graph = repository_graph.build(
                [a,b,c],
                imports,
                symbols,
            )

            refs = cross_reference.build(
                graph,
                symbols,
            )

            arch = architecture.analyze(
                graph,
            )

            change = impact.analyze(
                graph,
                ["core.py"],
            )

            plan = planner.plan(
                change,
                arch,
                graph,
            )

            memory.save(
                "repository-regression",
                {"plan":len(plan)},
            )

            loaded = memory.load(
                "repository-regression",
            )

            ok = (
                len(graph) == 3
                and len(refs) == 3
                and change["count"] == 3
                and len(plan) == 3
                and loaded["plan"] == 3
            )

            self._record(
                result,
                "Repository Intelligence",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Repository Intelligence",
                False,
            )


    def _autonomous_engineering_suite(self, result):

        try:

            from builder.engineering.knowledge_base import engine as knowledge
            from builder.engineering.decision_engine import engine as decision
            from builder.engineering.task_decomposer import engine as decomposer
            from builder.engineering.strategy_engine import engine as strategy
            from builder.engineering.multi_file_planner import planner
            from builder.engineering.autonomous_memory import memory

            repository = {
                "core.py":{
                    "imports":[],
                    "imported_by":["service.py"],
                },
                "service.py":{
                    "imports":["core.py"],
                    "imported_by":["api.py"],
                },
                "api.py":{
                    "imports":["service.py"],
                    "imported_by":[],
                },
            }

            knowledge.learn_pattern(
                "engineering",
                "repository-first",
            )

            d = decision.decide(
                {
                    "priority":"critical",
                    "repository_impact":True,
                    "architecture_change":True,
                    "new_feature":True,
                }
            )

            subtasks = decomposer.decompose(
                {
                    "title":"Builder Upgrade",
                    "priority":"high",
                }
            )

            impact = {
                "changed":["core.py"],
                "impacted":[
                    "core.py",
                    "service.py",
                    "api.py",
                ],
                "count":3,
            }

            architecture = {
                "hub_modules":[
                    "service.py",
                ],
            }

            s = strategy.strategy(
                d,
                impact,
                architecture,
            )

            plan = planner.plan(
                repository,
                impact,
                s,
            )

            memory.save(
                "engineering-regression",
                {
                    "tasks":len(subtasks),
                    "plan":len(plan),
                },
            )

            state = memory.load(
                "engineering-regression",
            )

            ok = (
                d["strategy"] == "architectural"
                and len(subtasks) == 6
                and len(plan) == 3
                and state["tasks"] == 6
                and state["plan"] == 3
            )

            self._record(
                result,
                "Autonomous Engineering",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Autonomous Engineering",
                False,
            )


    def _autonomous_code_generation_suite(self, result):

        try:

            from builder.codegen.intelligent_planner import planner as code_planner
            from builder.codegen.strategy_engine import engine as strategy_engine
            from builder.codegen.multi_file_generator import generator
            from builder.codegen.safe_modification import engine as safe
            from builder.codegen.incremental_evolution import engine as evolution
            from builder.codegen.autonomous_validator import validator

            plan = code_planner.plan(
                objective="Regression",
                strategy="architectural",
                impacted_files=[
                    "planner.py",
                    "executor.py",
                    "validator.py",
                ],
            )

            strategy = strategy_engine.strategy(
                "Regression",
                "architectural",
                plan,
            )

            outputs = generator.generate(
                strategy,
            )

            patch = safe.create_patch(
                "a=1",
                "a=2",
            )

            safe.apply(
                patch,
            )

            history = evolution.evolve(
                1,
                [
                    "planner",
                    "executor",
                    "validator",
                ],
            )

            validation = validator.summary(
                validator.validate(outputs)
            )

            ok = (
                len(plan) == 3
                and strategy["files"] == 3
                and len(outputs) == 3
                and safe.validate(patch)
                and history["current_version"] == 4
                and validation["success"] is True
            )

            self._record(
                result,
                "Autonomous Code Generation",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Autonomous Code Generation",
                False,
            )


    def _autonomous_review_suite(self, result):

        try:

            from builder.review.static_analysis import engine as static_analysis
            from builder.review.code_quality import engine as quality
            from builder.review.security import engine as security
            from builder.review.performance import engine as performance
            from builder.review.refactoring import engine as refactoring
            from builder.review.autonomous_review import engine as review

            source = """
import os

class Demo:

    def value(self):
        return 1

def helper():
    return 2
"""

            static_report = static_analysis.analyze(
                source,
            )

            quality_report = quality.analyze(
                source,
            )

            security_report = security.analyze(
                source,
            )

            performance_report = performance.analyze(
                source,
            )

            refactoring_report = refactoring.analyze(
                source,
            )

            autonomous = review.review(
                source,
            )

            summary = review.summary(
                autonomous,
            )

            ok = (
                static_report["functions"] == 2
                and quality_report["score"] == 100
                and security_report["score"] == 100
                and performance_report["score"] == 100
                and refactoring_report["count"] == 0
                and summary["passed"] is True
            )

            self._record(
                result,
                "Autonomous Review",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Autonomous Review",
                False,
            )


    def _autonomous_testing_suite(self, result):

        try:

            from builder.testing.intelligent_planner import planner
            from builder.testing.unit_generator import generator as unit_generator
            from builder.testing.integration_generator import generator as integration_generator
            from builder.testing.regression_generator import generator as regression_generator
            from builder.testing.prioritization import engine as prioritizer
            from builder.testing.orchestrator import engine as orchestrator

            impacted = [
                "builder/planning/planner.py",
                "builder/execution/executor.py",
                "builder/providers/runtime/router.py",
            ]

            plan = planner.plan(
                impacted,
            )

            unit = unit_generator.generate(
                plan,
            )

            integration = integration_generator.generate(
                plan,
            )

            regression = regression_generator.generate(
                impacted,
            )

            prioritized = prioritizer.prioritize(
                [
                    {
                        "module":"router",
                        "priority":"critical",
                        "type":"integration",
                    },
                    {
                        "module":"planner",
                        "priority":"high",
                        "type":"unit",
                    },
                    {
                        "module":"executor",
                        "priority":"normal",
                        "type":"regression",
                    },
                ]
            )

            execution = orchestrator.execute(
                unit,
                integration,
                regression,
                prioritized,
            )

            summary = orchestrator.summary(
                execution,
            )

            ok = (
                len(plan) == 3
                and len(unit) == 1
                and len(integration) == 2
                and len(regression) == 3
                and summary["total"] == 3
                and summary["passed"] == 3
            )

            self._record(
                result,
                "Autonomous Testing",
                ok,
            )

        except Exception:

            self._record(
                result,
                "Autonomous Testing",
                False,
            )


engine = RegressionEngine()
