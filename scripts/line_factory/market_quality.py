from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .project import Project, load_items
from .specs import load_market_quality


@dataclass
class MarketQualityResult:
    scores: dict[str, int] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    total_score: int = 0

    @property
    def ok(self) -> bool:
        return not self.failures


def audit_market_quality(project: Project) -> MarketQualityResult:
    rules = load_market_quality()
    dimensions = rules.get("dimensions") or {}
    readiness = rules.get("readiness") or {}
    result = MarketQualityResult()

    texts = collect_quality_text(project)
    manifest_entries = load_manifest_entries(project)
    required = [str(item) for item in rules.get("required_project_artifacts") or []]
    missing_required = [path for path in required if not (project.path / path).exists()]

    one_phrase = has_single_repeated_phrase(project)
    has_market_notes = (project.path / "reports" / "market_research_notes.md").exists()
    has_character_lock = (project.path / "reports" / "character_design_lock.md").exists()
    has_communication_plan = (project.path / "reports" / "item_communication_plan.md").exists()
    sheet_sources = manifest_mentions(manifest_entries, ("4x2", "sheet", "cropped into item source", "sheet crop"))
    detached_text = manifest_mentions(manifest_entries, ("generic detached", "detached label", "label box", "composited locally"))
    communication_intent = text_contains_any(texts, ("chat function", "emotional state", "camera", "meaning without text", "communication intent"))
    character_terms = text_contains_any(texts, ("silhouette", "face", "expression", "mascot", "character design", "signature"))
    market_terms = text_contains_any(texts, ("market", "LINE Store", "buyer", "competitor", "ranking", "current"))
    item_variety = estimate_item_variety(project)

    base_scores = {name: 10 for name in dimensions}
    if not has_character_lock:
        base_scores["character_appeal"] = min(base_scores.get("character_appeal", 10), 4)
        result.findings.append("Missing character design lock; character appeal cannot be proven.")
    if not character_terms:
        base_scores["character_appeal"] = min(base_scores.get("character_appeal", 10), 6)
        result.findings.append("Project notes do not describe silhouette, face, expression range, or mascot identity.")
    if not has_communication_plan:
        base_scores["communication_clarity"] = min(base_scores.get("communication_clarity", 10), 4)
        base_scores["pack_strategy"] = min(base_scores.get("pack_strategy", 10), 5)
        result.findings.append("Missing item communication plan; item intent is not defined separately from physical action.")
    if not communication_intent:
        base_scores["communication_clarity"] = min(base_scores.get("communication_clarity", 10), 6)
        result.findings.append("Project notes do not prove meaning is readable without text.")
    if item_variety < 0.65:
        base_scores["expression_variety"] = min(base_scores.get("expression_variety", 10), 5)
        result.findings.append(f"Item descriptions appear low-variety ({item_variety:.2f}); check repeated poses or prop swaps.")
    if one_phrase and not has_communication_plan:
        base_scores["pack_strategy"] = min(base_scores.get("pack_strategy", 10), 4)
        result.findings.append("One-phrase pack lacks documented distinct emotional or use-case nuances.")
    if detached_text:
        base_scores["text_integration"] = min(base_scores.get("text_integration", 10), 4)
        result.findings.append("Source manifest suggests detached or locally composited label-style text.")
    if not has_market_notes:
        base_scores["current_market_fit"] = min(base_scores.get("current_market_fit", 10), 4)
        result.findings.append("Missing current market research notes.")
    if not market_terms:
        base_scores["current_market_fit"] = min(base_scores.get("current_market_fit", 10), 6)
        result.findings.append("Project notes do not record current LINE Store or buyer-fit observations.")
    if sheet_sources:
        base_scores["style_consistency"] = min(base_scores.get("style_consistency", 10), 5)
        base_scores["composition_and_readability"] = min(base_scores.get("composition_and_readability", 10), 6)
        result.findings.append("Final sources appear to derive from sheet/cell generation, which is low-control for final production.")
    if missing_required:
        result.findings.append("Missing market-grade artifact(s): " + ", ".join(missing_required))

    result.scores = {name: max(0, min(10, int(score))) for name, score in base_scores.items()}
    result.total_score = weighted_total(result.scores, dimensions)

    min_total = int(readiness.get("min_total_score", 80))
    min_dimension = int(readiness.get("min_dimension_score", 7))
    fatal_below = int(readiness.get("fatal_if_any_dimension_below", 5))

    for name, score in sorted(result.scores.items()):
        configured_min = int((dimensions.get(name) or {}).get("min_score", min_dimension))
        if score < fatal_below:
            result.failures.append(f"{name}: score {score}/10 is below fatal threshold {fatal_below}.")
        elif score < configured_min:
            result.failures.append(f"{name}: score {score}/10 is below required {configured_min}.")
    if result.total_score < min_total:
        result.failures.append(f"total score {result.total_score}/100 is below required {min_total}.")
    if missing_required:
        result.failures.append("required market-grade artifacts are missing.")
    for pattern in rules.get("automatic_failure_patterns") or []:
        if pattern_matches_project(str(pattern), sheet_sources, detached_text, one_phrase, item_variety, texts):
            result.failures.append(f"automatic failure pattern: {pattern}")

    if result.failures:
        result.recommendations.extend(
            [
                "Do not mark this project ready for manual upload.",
                "Create market research notes, character design lock, and item communication plan before final art production.",
                "Generate final artwork one item at a time unless a stricter high-control batch method is documented.",
                "Treat generic detached text labels as emergency fallback, not production quality.",
            ]
        )
    else:
        result.recommendations.append("Market-grade QA passed; still perform final human visual confirmation before upload.")
    return result


def build_market_quality_report(project: Project, result: MarketQualityResult | None = None) -> str:
    rules = load_market_quality()
    result = result or audit_market_quality(project)
    lines = [
        f"# Market Quality Report: {project.name}",
        "",
        "This report is separate from technical validation. It estimates whether a valid ZIP is plausibly market-grade.",
        "",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        f"- Total score: {result.total_score}/100",
        "",
        "## Dimension Scores",
    ]
    dimensions = rules.get("dimensions") or {}
    for name, score in result.scores.items():
        weight = (dimensions.get(name) or {}).get("weight", "?")
        lines.append(f"- {name}: {score}/10 (weight {weight})")
    lines.extend(["", "## Failures"])
    lines.extend([f"- {failure}" for failure in result.failures] or ["- None"])
    lines.extend(["", "## Findings"])
    lines.extend([f"- {finding}" for finding in result.findings] or ["- None"])
    lines.extend(["", "## Recommendations"])
    lines.extend([f"- {item}" for item in result.recommendations] or ["- None"])
    lines.append("")
    text = "\n".join(lines)
    project.reports_dir.mkdir(parents=True, exist_ok=True)
    (project.reports_dir / "market_quality.md").write_text(text, encoding="utf-8")
    return text


def weighted_total(scores: dict[str, int], dimensions: dict[str, Any]) -> int:
    total_weight = 0
    weighted = 0.0
    for name, score in scores.items():
        weight = int((dimensions.get(name) or {}).get("weight", 1))
        total_weight += weight
        weighted += (score / 10) * weight
    if total_weight == 0:
        return 0
    return int(round((weighted / total_weight) * 100))


def collect_quality_text(project: Project) -> str:
    paths = [
        project.path / "brief.md",
        project.path / "approvals.md",
        project.path / "reports" / "market_research_notes.md",
        project.path / "reports" / "character_design_lock.md",
        project.path / "reports" / "item_communication_plan.md",
        project.path / "assets" / "working" / "source_manifest.yml",
    ]
    parts = []
    for path in paths:
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    item_path = project.path / "items.csv"
    if item_path.exists():
        parts.append(item_path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts).lower()


def load_manifest_entries(project: Project) -> list[dict[str, Any]]:
    manifest = project.working_dir / "source_manifest.yml"
    if not manifest.exists():
        return []
    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    except Exception:
        return []
    entries = data.get("items") if isinstance(data, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def manifest_mentions(entries: list[dict[str, Any]], needles: tuple[str, ...]) -> bool:
    for entry in entries:
        text = " ".join(str(value) for value in entry.values()).lower()
        if any(needle.lower() in text for needle in needles):
            return True
    return False


def text_contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle.lower() in text for needle in needles)


def has_single_repeated_phrase(project: Project) -> bool:
    phrases = [item.text for item in load_items(project) if item.text]
    return bool(phrases) and len(set(phrases)) == 1


def estimate_item_variety(project: Project) -> float:
    try:
        rows = load_items(project)
    except Exception:
        return 0.0
    descriptions = [row.description.strip() for row in rows if row.description.strip()]
    if not descriptions:
        return 0.0
    normalized = {description[:8] for description in descriptions}
    unique_ratio = len(normalized) / len(descriptions)
    avg_length = sum(len(description) for description in descriptions) / len(descriptions)
    length_factor = min(1.0, avg_length / 18)
    return (unique_ratio * 0.7) + (length_factor * 0.3)


def pattern_matches_project(
    pattern: str,
    sheet_sources: bool,
    detached_text: bool,
    one_phrase: bool,
    item_variety: float,
    texts: str,
) -> bool:
    lower = pattern.lower()
    if "4x2 sheet" in lower or "sheet art" in lower:
        return sheet_sources
    if "generic detached text label" in lower:
        return detached_text
    if "fewer than six" in lower:
        return item_variety < 0.65
    if "only make sense after reading" in lower:
        return one_phrase and "meaning without text" not in texts
    if "plain object icon" in lower:
        return "object icon" in texts or ("generic object" in texts and "signature" not in texts)
    return False
