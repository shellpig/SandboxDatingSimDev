class SandboxDatingSimError(Exception):
    """Base exception for Sandbox Dating Sim."""
    pass

class ValidationError(SandboxDatingSimError):
    """Raised when validation fails."""
    pass

class SetupPackageError(SandboxDatingSimError):
    """Raised when there is an error with the Setup Package."""
    pass

class MarkdownParseError(SandboxDatingSimError):
    """Raised when there is an error parsing Markdown."""
    pass
