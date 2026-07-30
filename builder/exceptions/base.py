class BuilderError(Exception):
    """Base exception for Vidhi Builder."""


class ConfigurationError(BuilderError):
    """Configuration error."""


class BootstrapError(BuilderError):
    """Bootstrap error."""


class WorkspaceError(BuilderError):
    """Workspace error."""


class ValidationError(BuilderError):
    """Validation error."""
