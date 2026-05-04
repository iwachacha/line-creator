from __future__ import annotations

import csv

from .project import Project
from .specs import load_review_risk


def build_risk_report(project: Project) -> str:
    risk = load_review_risk()
    checklist = risk.get("checklist", [])
    manual = risk.get("manual_review_required", [])
    findings = scan_project_risks(project, risk)
    lines = [
        f"# Risk Report: {project.name}",
        "",
        "This report is a checklist aid and does not guarantee LINE review approval.",
        "",
        "## Project-Specific Findings",
    ]
    lines.extend([f"- {finding}" for finding in findings] or ["- None detected by keyword scan."])
    lines.extend(
        [
            "",
            "Review findings manually in HAG-2 and again in HAG-5. Keyword absence is not approval.",
            "",
            "## Required Human Review",
        ]
    )
    for item in manual:
        lines.append(f"- [ ] {item}")
    lines.extend(["", "## Review Checklist"])
    for item in checklist:
        lines.append(f"- [ ] {item}")
    lines.extend(["", "## HAG Status", "Confirm HAG-5 before manual ZIP upload."])
    text = "\n".join(lines) + "\n"
    project.reports_dir.mkdir(parents=True, exist_ok=True)
    (project.reports_dir / "risk_report.md").write_text(text, encoding="utf-8")
    return text


def scan_project_risks(project: Project, risk: dict) -> list[str]:
    haystacks = collect_project_text(project)
    keyword_groups: dict[str, list[str]] = {}
    for group_name in ("fatal_keywords", "review_keywords"):
        for group, values in (risk.get(group_name) or {}).items():
            keyword_groups[group] = [str(value) for value in values]

    findings: list[str] = []
    for source, text in haystacks.items():
        lowered = text.lower()
        for group, values in keyword_groups.items():
            for keyword in values:
                if keyword.lower() in lowered:
                    findings.append(f"{source}: `{keyword}` matched {group} review-risk keywords")
                    break
    return sorted(set(findings))


def collect_project_text(project: Project) -> dict[str, str]:
    texts = {"project.yml metadata": "\n".join(project.metadata.values())}
    brief = project.path / "brief.md"
    if brief.exists():
        texts["brief.md"] = brief.read_text(encoding="utf-8", errors="replace")
    items = project.path / "items.csv"
    if items.exists():
        rows = []
        with items.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                rows.append(" ".join(str(value or "") for value in row.values()))
        texts["items.csv"] = "\n".join(rows)
    return texts
