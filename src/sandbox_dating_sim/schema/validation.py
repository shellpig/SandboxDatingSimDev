from pydantic import BaseModel

class Issue(BaseModel):
    severity: str  # "error" | "warning"
    type: str
    path: str
    message: str
    suggested_action: str | None = None

class ValidationReport(BaseModel):
    status: str  # "passed" | "failed"
    issues: list[Issue] = []

    @classmethod
    def from_issues(cls, issues: list[Issue]) -> "ValidationReport":
        status = "failed" if any(i.severity == "error" for i in issues) else "passed"
        return cls(status=status, issues=issues)
