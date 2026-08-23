from dataclasses import dataclass


class ProjectServiceError(RuntimeError):
    """A project operation failed in a way the UI can safely report."""


@dataclass(frozen=True)
class ProjectResult:
    ok: bool
    message: str
    project_id: str | None = None


@dataclass(frozen=True)
class ProjectReportResult:
    ok: bool
    message: str
    report_id: str | None = None


@dataclass(frozen=True)
class ViewCountResult:
    ok: bool
    counted: bool
