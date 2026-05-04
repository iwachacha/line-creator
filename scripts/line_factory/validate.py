from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from PIL import Image

from .images import (
    alpha_bbox,
    alpha_coverage,
    average_hash,
    chroma_key_edge_ratio,
    corner_alpha_values,
    edge_alpha_coverage,
    hamming,
    has_transparency,
    opaque_bbox_fill_ratio,
    open_png,
    visible_luma_delta,
)
from .project import Project, load_items
from .specs import ExpectedImage, expected_images, load_kind_spec, load_quality_thresholds


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


def validate_project(project: Project) -> ValidationResult:
    spec = load_kind_spec(project.kind)
    thresholds = load_quality_thresholds()
    result = ValidationResult()
    expected = expected_images(project.kind, project.count, spec)
    existing = {p.name: p for p in project.final_dir.glob("*.png")}
    max_image_bytes = int(spec["limits"]["max_image_bytes"])

    for exp in expected:
        path = existing.get(exp.filename)
        if not path:
            result.add_error(f"Missing required file: {exp.filename}")
            continue
        validate_image_file(path, exp, max_image_bytes, result, project.kind, thresholds)

    extra = sorted(set(existing) - {e.filename for e in expected})
    for name in extra:
        result.add_warning(f"Unexpected PNG in final directory: {name}")

    check_approvals(project, result)
    check_line_metadata(project, spec, result, thresholds)
    check_suspect_text(project, result, thresholds)
    check_source_traceability(project, result)
    item_paths = [existing[e.filename] for e in expected if e.role == "item" and e.filename in existing]
    check_duplicates(item_paths, result, thresholds)
    result.info.append(f"Validated {len(existing)} final PNG file(s).")
    return result


def check_approvals(project: Project, result: ValidationResult) -> None:
    for gate, state in project.approvals.items():
        if state == "approved":
            result.info.append(f"{gate}: approved")
        else:
            result.add_error(f"{gate}: approval pending; package blocked")


def check_line_metadata(project: Project, spec: dict, result: ValidationResult, thresholds: dict) -> None:
    limits = spec.get("text_limits", {})
    metadata = project.metadata
    for field_name, value in metadata.items():
        limit = int(limits.get(field_name, 0) or 0)
        if not value:
            result.add_error(f"metadata.{field_name}: required field is blank")
            continue
        if limit and len(value) > limit:
            result.add_error(f"metadata.{field_name}: {len(value)} characters exceeds LINE limit {limit}")
        if len(value) <= 2 and field_name != "copyright":
            result.add_warning(f"metadata.{field_name}: unusually short; human review recommended")
        if re.search(r"https?://|www\.|\.com\b|\.jp\b", value, re.IGNORECASE):
            result.add_warning(f"metadata.{field_name}: URL-like text found; advertising/review risk")
        if re.search(r"\b(sale|discount|campaign|limited time|free|buy now|follow|subscribe)\b", value, re.IGNORECASE):
            result.add_warning(f"metadata.{field_name}: advertising-like wording found; review risk")
        if re.search(r"[\u2600-\u27BF\U0001F300-\U0001FAFF]", value):
            result.add_warning(f"metadata.{field_name}: emoji or device-dependent symbol found; LINE metadata review recommended")


def check_suspect_text(project: Project, result: ValidationResult, thresholds: dict) -> None:
    meta = thresholds.get("metadata", {})
    tokens = meta.get("warn_suspect_text_tokens", [])
    patterns = meta.get("warn_suspect_text_patterns", [])
    files = [
        project.path / "project.yml",
        project.path / "brief.md",
        project.path / "items.csv",
    ]
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token and token in text:
                result.add_warning(f"{path.name}: suspect text token `{token}` found; check for mojibake or placeholder text")
                break
        for pattern in patterns:
            if pattern and re.search(pattern, text, re.IGNORECASE):
                result.add_warning(f"{path.name}: suspect text pattern `{pattern}` found; check placeholders or malformed text")
                break


def check_source_traceability(project: Project, result: ValidationResult) -> None:
    try:
        items = load_items(project)
    except Exception as exc:
        result.add_error(f"items.csv: cannot read item rows ({exc})")
        return
    if len(items) < project.count:
        result.add_error(f"items.csv: need {project.count} item rows, found {len(items)}")
    for item in items[: project.count]:
        source_name = item.source_file or f"source_{item.index:02d}.png"
        source_path = project.source_dir / source_name
        if not source_path.exists():
            result.add_error(f"items.csv row {item.index}: declared source_file missing: {source_name}")
            continue
        try:
            img = open_png(source_path)
        except Exception as exc:
            result.add_error(f"{source_name}: cannot open declared source PNG ({exc})")
            continue
        if not has_transparency(img):
            result.add_warning(f"{source_name}: source image has no transparency; check background removal before HAG-5")
        if opaque_bbox_fill_ratio(img) > 0.98 and alpha_coverage(img) > 0.75:
            result.add_warning(f"{source_name}: opaque rectangular source coverage suggests unremoved background")
        result.info.append(f"source mapping: item {item.index:02d} -> {source_name}")
        img.close()
    manifest = project.working_dir / "source_manifest.yml"
    if not manifest.exists():
        result.add_warning("assets/working/source_manifest.yml missing; HAG-5 traceability review should record raw source evidence")
        return
    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        result.add_warning(f"assets/working/source_manifest.yml cannot be parsed ({exc})")
        return
    entries = data.get("items") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        result.add_warning("assets/working/source_manifest.yml has no `items` list")
        return
    manifest_sources = {str(entry.get("source_file") or "") for entry in entries if isinstance(entry, dict)}
    for item in items[: project.count]:
        source_name = item.source_file or f"source_{item.index:02d}.png"
        if source_name not in manifest_sources:
            result.add_warning(f"assets/working/source_manifest.yml missing entry for {source_name}")


def validate_image_file(
    path: Path,
    expected: ExpectedImage,
    max_image_bytes: int,
    result: ValidationResult,
    kind: str,
    thresholds: dict,
) -> None:
    if path.stat().st_size > max_image_bytes:
        result.add_error(f"{path.name}: file size exceeds 1 MB")
    try:
        img = open_png(path)
    except Exception as exc:
        result.add_error(f"{path.name}: cannot open PNG ({exc})")
        return
    if img.format != "PNG":
        result.add_error(f"{path.name}: not a PNG file")
    if img.mode not in ("RGBA", "RGB", "P", "LA"):
        result.add_error(f"{path.name}: unsupported color mode {img.mode}")
    width, height = img.size
    if expected.width is not None and width != expected.width:
        result.add_error(f"{path.name}: width {width} != {expected.width}")
    if expected.height is not None and height != expected.height:
        result.add_error(f"{path.name}: height {height} != {expected.height}")
    if expected.max_width is not None and width > expected.max_width:
        result.add_error(f"{path.name}: width {width} exceeds {expected.max_width}")
    if expected.max_height is not None and height > expected.max_height:
        result.add_error(f"{path.name}: height {height} exceeds {expected.max_height}")
    if expected.even_dimensions and (width % 2 or height % 2):
        result.add_error(f"{path.name}: dimensions must be even numbers")
    if expected.required_alpha and not has_transparency(img):
        result.add_error(f"{path.name}: item image must have transparency")
    if expected.role == "item":
        bbox = alpha_bbox(img)
        if bbox is None:
            result.add_error(f"{path.name}: no visible non-transparent content")
        else:
            ratio = ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / (width * height)
            key = "min_nontransparent_bbox_ratio_emoji" if kind == "regular_emoji" else "min_nontransparent_bbox_ratio_sticker"
            if ratio < float(thresholds["visibility"][key]):
                result.add_warning(f"{path.name}: visible content is small ({ratio:.2f})")
        coverage = alpha_coverage(img)
        if coverage < float(thresholds["visibility"]["min_alpha_coverage_ratio"]):
            result.add_warning(f"{path.name}: low alpha coverage ({coverage:.2f})")
        edge_ratio = edge_alpha_coverage(img)
        if edge_ratio > float(thresholds["visibility"].get("warn_edge_alpha_coverage_ratio_above", 0.02)):
            result.add_warning(f"{path.name}: visible pixels touch image edges ({edge_ratio:.2f}); crop/background risk")
        corners = corner_alpha_values(img)
        if corners and max(corners) > int(thresholds["visibility"].get("warn_corner_alpha_above", 8)):
            result.add_warning(f"{path.name}: opaque corner pixels found; check for unremoved background")
        if opaque_bbox_fill_ratio(img) > float(thresholds["visibility"].get("warn_opaque_bbox_fill_ratio_above", 0.98)):
            result.add_warning(f"{path.name}: visible bounding box is almost fully opaque; possible rectangular background")
        chroma_colors = [(0, 255, 0), (255, 0, 255)]
        chroma_ratio = chroma_key_edge_ratio(img, chroma_colors)
        if chroma_ratio > float(thresholds["visibility"].get("warn_chroma_key_edge_ratio_above", 0.01)):
            result.add_warning(f"{path.name}: possible chroma-key residue on edges ({chroma_ratio:.2f})")
        min_delta = float(thresholds["visibility"].get("warn_low_contrast_luma_delta", 0))
        if min_delta:
            light_delta = visible_luma_delta(img, (255, 255, 255))
            dark_delta = visible_luma_delta(img, (32, 32, 32))
            if light_delta < min_delta or dark_delta < min_delta:
                result.add_warning(f"{path.name}: low contrast against chat backgrounds; light delta {light_delta:.1f}, dark delta {dark_delta:.1f}")
    img.close()


def check_duplicates(paths: list[Path], result: ValidationResult, thresholds: dict) -> None:
    if len(paths) < 2:
        return
    hashes = []
    for path in paths:
        with Image.open(path) as img:
            hashes.append((path.name, average_hash(img), average_visible_rgb(img)))
    threshold = int(thresholds["duplicates"]["warn_average_hash_hamming_distance_below"])
    color_threshold = float(thresholds["duplicates"].get("warn_average_color_distance_below", 35))
    for i, (name_a, hash_a, color_a) in enumerate(hashes):
        for name_b, hash_b, color_b in hashes[i + 1 :]:
            color_distance = sum((a - b) ** 2 for a, b in zip(color_a, color_b)) ** 0.5
            if hamming(hash_a, hash_b) < threshold and color_distance < color_threshold:
                result.add_warning(f"{name_a} and {name_b}: visually similar; human review recommended")


def average_visible_rgb(img: Image.Image) -> tuple[float, float, float]:
    rgba = img.convert("RGBA")
    pixels = [(r, g, b) for r, g, b, a in rgba.getdata() if a > 24]
    if not pixels:
        return (0.0, 0.0, 0.0)
    total = len(pixels)
    return (
        sum(pixel[0] for pixel in pixels) / total,
        sum(pixel[1] for pixel in pixels) / total,
        sum(pixel[2] for pixel in pixels) / total,
    )
