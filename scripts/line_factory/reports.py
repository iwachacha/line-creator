from __future__ import annotations

from .project import Project
from .risk_report import build_risk_report
from .validate import ValidationResult, validate_project
from .visual_report import build_visual_report


def write_validation_report(project: Project, result: ValidationResult | None = None) -> str:
    result = result or validate_project(project)
    lines = [
        f"# Validation Report: {project.name}",
        "",
        f"- Kind: `{project.kind}`",
        f"- Count: `{project.count}`",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        "",
        "## Fatal Errors",
    ]
    lines.extend([f"- {e}" for e in result.errors] or ["- None"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend([f"- {w}" for w in result.warnings] or ["- None"])
    lines.append("")
    lines.append("## Info")
    lines.extend([f"- {i}" for i in result.info] or ["- None"])
    lines.append("")
    lines.append("## Human Approval")
    for gate, state in project.approvals.items():
        lines.append(f"- {gate}: {state}")
    lines.append("")
    lines.append("All HAG-1 through HAG-5 entries must be `approved` in `project.yml` before ZIP creation.")
    text = "\n".join(lines) + "\n"
    project.reports_dir.mkdir(parents=True, exist_ok=True)
    (project.reports_dir / "validation.md").write_text(text, encoding="utf-8")
    return text


def build_all_reports(project: Project) -> ValidationResult:
    result = validate_project(project)
    write_validation_report(project, result)
    build_risk_report(project)
    build_visual_report(project)
    return result
