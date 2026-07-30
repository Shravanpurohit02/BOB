from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from .approval import Approval
from .report import EngineeringReport
from .repository import RepositoryAnalysis
from .risk import Risk
from .rollback import RollbackPlan
from .validation import ValidationSummary

from builder.reflection.semantic_models import SemanticRepository
from builder.planning.models import EngineeringPlan
from builder.intelligence.models import ImpactReport


@dataclass(slots=True)
class ChangeFile:
    path: str
    action: str
    reason: str = ""


@dataclass(slots=True)
class EngineeringChangeSet:

    id: str = field(default_factory=lambda: uuid4().hex)

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    objective: str = ""

    status: str = "draft"

    files: list[ChangeFile] = field(default_factory=list)

    repository: RepositoryAnalysis = field(
        default_factory=RepositoryAnalysis
    )

    validation: ValidationSummary = field(
        default_factory=ValidationSummary
    )

    report: EngineeringReport = field(
        default_factory=EngineeringReport
    )

    approval: Approval = field(
        default_factory=Approval
    )

    rollback: RollbackPlan = field(
        default_factory=RollbackPlan
    )

    risks: list[Risk] = field(default_factory=list)



    semantic: SemanticRepository | None = None

    plan: EngineeringPlan | None = None

    impact: ImpactReport | None = None

    testing: dict = field(default_factory=dict)


    metadata: dict = field(default_factory=dict)
