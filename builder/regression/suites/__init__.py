"""
Regression suite registry.

Each suite exports:

    run() -> bool

RegressionEngine imports this registry and executes the suites in order.
"""

from collections import OrderedDict

from .autonomous_code_evolution import run as autonomous_code_evolution
from .autonomous_code_generation import run as autonomous_code_generation
from .autonomous_engineering import run as autonomous_engineering
from .autonomous_review import run as autonomous_review
from .autonomous_testing import run as autonomous_testing
from .cli import run as cli
from .code_library_ingestion import run as code_library_ingestion
from .code_library_retrieval import run as code_library_retrieval
from .code_library_composition import run as code_library_composition
from .context_intelligence import run as context_intelligence
from .decision_engine import run as decision_engine
from .dependency_graph import run as dependency_graph
from .end_to_end_builder import run as end_to_end_builder
from .execution import run as execution
from .execution_analytics import run as execution_analytics
from .failure_classification import run as failure_classification
from .multi_agent_coordination import run as multi_agent_coordination
from .orchestrator import run as orchestrator
from .output import run as output
from .parallel_scheduler import run as parallel_scheduler
from .patch import run as patch
from .pipeline import run as pipeline
from .planning_intelligence import run as planning_intelligence
from .provider_execution import run as provider_execution
from .provider_runtime import run as provider_runtime
from .recovery_stress import run as recovery_stress
from .repository_engineering import run as repository_engineering
from .repository_intelligence import run as repository_intelligence
from .resource_manager import run as resource_manager
from .resume import run as resume
from .review import run as review
from .runtime import run as runtime
from .self_healing_execution import run as self_healing_execution
from .semantic_repository import run as semantic_repository
from .snapshot import run as snapshot
from .transaction import run as transaction
from .worker_pool import run as worker_pool
from .worker_recovery import run as worker_recovery
from .validation_pipeline_contract import run as validation_pipeline_contract
from .code_library_application_composition import run as code_library_application_composition

SUITES = OrderedDict(
    [
        ("Patch", patch),
        ("Review", review),
        ("Output", output),
        ("Pipeline", pipeline),
        ("CLI", cli),
        ("Execution", execution),
        ("Autonomous Runtime", runtime),
        ("Transaction", transaction),
        ("Execution Snapshot", snapshot),
        ("Execution Resume", resume),
        ("Recovery Stress", recovery_stress),
        ("Orchestrator", orchestrator),
        ("Parallel Scheduler", parallel_scheduler),
        ("Worker Pool", worker_pool),
        ("Resource Manager", resource_manager),
        ("Worker Recovery", worker_recovery),
        ("Planning Intelligence", planning_intelligence),
        ("Dependency Graph", dependency_graph),
        ("Failure Classification", failure_classification),
        ("Self-Healing Execution", self_healing_execution),
        ("Execution Analytics", execution_analytics),
        ("Decision Engine", decision_engine),
        ("Autonomous Code Evolution", autonomous_code_evolution),
        ("Multi-Agent Coordination", multi_agent_coordination),
        ("Repository Engineering", repository_engineering),
        ("End-to-End Builder", end_to_end_builder),
        ("Provider Runtime", provider_runtime),
        ("Provider Execution", provider_execution),
        ("Context Intelligence", context_intelligence),
        ("Semantic Repository", semantic_repository),
        ("Repository Intelligence", repository_intelligence),
        ("Code Library Ingestion", code_library_ingestion),
        ("Code Library Retrieval", code_library_retrieval),
        ("Code Library Composition", code_library_composition),
        ("Code Library Application Composition", code_library_application_composition),
        ("Autonomous Engineering", autonomous_engineering),
        ("Autonomous Code Generation", autonomous_code_generation),
        ("Autonomous Review", autonomous_review),
        ("Validation Pipeline Contract", validation_pipeline_contract),
        ("Autonomous Testing", autonomous_testing),
    ]
)

__all__ = [
    "SUITES",
]
