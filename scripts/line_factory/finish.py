from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from .contact_sheet import build_contact_sheet
from .images import fit_to_canvas, fit_within_max, list_source_pngs, open_png, save_png
from .project import Project, load_items
from .specs import expected_images, load_kind_spec


class FinishError(RuntimeError):
    pass


def clear_final_dir(final_dir: Path) -> None:
    final_dir.mkdir(parents=True, exist_ok=True)
    for p in final_dir.glob("*.png"):
        p.unlink()


def finish_project(project: Project) -> list[Path]:
    spec = load_kind_spec(project.kind)
    source_pngs = list_source_pngs(project.source_dir)
    source_by_name = {p.name: p for p in source_pngs}
    sources = resolve_item_sources(project, source_pngs, source_by_name)

    clear_final_dir(project.final_dir)
    outputs: list[Path] = []
    item_specs = [e for e in expected_images(project.kind, project.count, spec) if e.role == "item"]
    margin = int(spec.get("layout", {}).get("recommended_margin_px", 0))
    source_map = []
    for source, expected in zip(sources, item_specs):
        img = open_png(source)
        if project.kind == "static_sticker":
            out = fit_within_max(img, int(expected.max_width or 370), int(expected.max_height or 320), margin)
        else:
            out = fit_to_canvas(img, int(expected.width or 180), int(expected.height or 180), margin)
        dest = project.final_dir / expected.filename
        save_png(out, dest)
        outputs.append(dest)
        source_map.append({"final_file": expected.filename, "source_file": source.name})

    first = open_png(sources[0])
    if project.kind == "static_sticker":
        main = fit_to_canvas(first, spec["images"]["main"]["width"], spec["images"]["main"]["height"], 0)
        tab = fit_to_canvas(first, spec["images"]["tab"]["width"], spec["images"]["tab"]["height"], 0)
        save_png(main, project.final_dir / spec["images"]["main"]["filename"])
        save_png(tab, project.final_dir / spec["images"]["tab"]["filename"])
        source_map.insert(0, {"final_file": spec["images"]["tab"]["filename"], "source_file": sources[0].name})
        source_map.insert(0, {"final_file": spec["images"]["main"]["filename"], "source_file": sources[0].name})
    else:
        tab = fit_to_canvas(first, spec["images"]["tab"]["width"], spec["images"]["tab"]["height"], 0)
        save_png(tab, project.final_dir / spec["images"]["tab"]["filename"])
        source_map.insert(0, {"final_file": spec["images"]["tab"]["filename"], "source_file": sources[0].name})

    (project.reports_dir / "source_mapping.yml").write_text(
        yaml.safe_dump({"items": source_map}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    build_contact_sheet(project)
    return sorted(project.final_dir.glob("*.png"))


def resolve_item_sources(project: Project, source_pngs: list[Path], source_by_name: dict[str, Path]) -> list[Path]:
    items = load_items(project)
    if len(items) < project.count:
        raise FinishError(f"Need {project.count} item rows in items.csv, found {len(items)}")
    resolved: list[Path] = []
    missing: list[str] = []
    for item in items[: project.count]:
        declared = item.source_file or f"source_{item.index:02d}.png"
        path = source_by_name.get(declared)
        if path is None:
            missing.append(declared)
        else:
            resolved.append(path)
    if missing:
        raise FinishError(f"Missing declared source PNG(s): {', '.join(missing)}")
    if len(resolved) >= project.count:
        return resolved[: project.count]
    if len(source_pngs) < project.count:
        raise FinishError(f"Need at least {project.count} source PNGs, found {len(source_pngs)} in {project.source_dir}")
    return source_pngs[: project.count]
