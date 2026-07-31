from __future__ import annotations

from .config import GuardrailConfig
from .engine import GuardrailEngine
from .registry import ValidatorRegistry

from .validators.api import APIValidator
from .validators.duplicates import DuplicateValidator
from .validators.files import FileValidator
from .validators.imports import ImportValidator
from .validators.path import PathValidator
from .validators.quality import QualityValidator
from .validators.schema import SchemaValidator
from .validators.security import SecurityValidator
from .validators.syntax import SyntaxValidator


def create_guardrail_engine(
    config: GuardrailConfig | None = None,
) -> GuardrailEngine:
    """
    Factory for a fully configured GuardrailEngine.
    """

    config = config or GuardrailConfig()

    registry = ValidatorRegistry(config)

    registry.register(SchemaValidator(config))
    registry.register(PathValidator(config))
    registry.register(FileValidator(config))
    registry.register(SyntaxValidator(config))
    registry.register(ImportValidator(config))
    registry.register(DuplicateValidator(config))
    registry.register(APIValidator(config))
    registry.register(QualityValidator(config))
    registry.register(SecurityValidator(config))

    return GuardrailEngine(
        registry=registry,
        config=config,
    )
