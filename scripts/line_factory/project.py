from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .specs import ROOT, SpecError, valid_count


TEMPLATE_DIR = ROOT / "projects" / "_template"
REQUIRED_HAGS = ("HAG-1", "HAG-2", "HAG-3", "HAG-4", "HAG-5")


@dataclass(frozen=True)
class Item:
    index: int
    type: str
    text: str
    description: str
    status: str
    source_file: str


@dataclass(frozen=True)
class Project:
    path: Path
    config: dict[str, Any]

    @property
    def name(self) -> str:
        return str(self.config.get("name") or self.path.name)

    @property
    def kind(self) -> str:
        return str(self.config.get("kind", "static_sticker"))

    @property
    def count(self) -> int:
        return int(self.config.get("count", 8))

    @property
    def source_dir(self) -> Path:
        return self.path / "assets" / "source"

    @property
    def working_dir(self) -> Path:
        return self.path / "assets" / "working"

    @property
    def final_dir(self) -> Path:
        return self.path / "assets" / "final"

    @property
    def reports_dir(self) -> Path:
        return self.path / "reports"

    @property
    def dist_dir(self) -> Path:
        return self.path / "dist"

    @property
    def approvals(self) -> dict[str, str]:
        raw = self.config.get("approvals") or {}
        if not isinstance(raw, dict):
            return {gate: "pending" for gate in REQUIRED_HAGS}
        return {gate: str(raw.get(gate, "pending")).strip().lower() for gate in REQUIRED_HAGS}

    @property
    def pending_approvals(self) -> list[str]:
        return [gate for gate, state in self.approvals.items() if state != "approved"]

    @property
    def metadata(self) -> dict[str, str]:
        keys = ("creator_name", "title", "description", "copyright")
        return {key: str(self.config.get(key) or "").strip() for key in keys}


def ensure_project_dirs(path: Path) -> None:
    for sub in ["assets/source", "assets/working", "assets/final", "reports", "dist"]:
        (path / sub).mkdir(parents=True, exist_ok=True)


def load_project(project_path: str | Path) -> Project:
    path = Path(project_path).resolve()
    cfg_path = path / "project.yml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing project.yml: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    if not isinstance(config, dict):
        raise SpecError(f"project.yml must be a mapping: {cfg_path}")
    project = Project(path=path, config=config)
    if not valid_count(project.kind, project.count):
        raise SpecError(f"Invalid count {project.count} for {project.kind}")
    ensure_project_dirs(path)
    return project


def init_project(project_path: str | Path, kind: str, count: int, force: bool = False) -> Project:
    path = Path(project_path).resolve()
    if path.exists() and any(path.iterdir()) and not force:
        raise FileExistsError(f"Project already exists and is not empty: {path}")
    if not valid_count(kind, count):
        raise SpecError(f"Invalid count {count} for {kind}")
    if path.exists() and force:
        projects_root = (ROOT / "projects").resolve()
        try:
            path.relative_to(projects_root)
        except ValueError as exc:
            raise SpecError(f"Refusing init --force outside projects/: {path}") from exc
        shutil.rmtree(path)
    shutil.copytree(TEMPLATE_DIR, path)
    cfg_path = path / "project.yml"
    with cfg_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    config["name"] = path.name
    config["kind"] = kind
    config["count"] = count
    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    write_default_items(path / "items.csv", count)
    ensure_project_dirs(path)
    return load_project(path)


def write_default_items(path: Path, count: int) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "type", "text", "description", "status", "source_file"])
        writer.writeheader()
        for index in range(1, count + 1):
            writer.writerow(
                {
                    "index": index,
                    "type": "item",
                    "text": "",
                    "description": f"Item {index}",
                    "status": "draft",
                    "source_file": f"source_{index:02d}.png",
                }
            )


def load_items(project: Project) -> list[Item]:
    items_path = project.path / "items.csv"
    if not items_path.exists():
        raise FileNotFoundError(f"Missing items.csv: {items_path}")
    items: list[Item] = []
    with items_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_type = (row.get("type") or "item").strip() or "item"
            if item_type != "item":
                continue
            raw_index = row.get("index") or str(len(items) + 1)
            items.append(
                Item(
                    index=int(raw_index),
                    type=item_type,
                    text=(row.get("text") or "").strip(),
                    description=(row.get("description") or "").strip(),
                    status=(row.get("status") or "").strip(),
                    source_file=(row.get("source_file") or "").strip(),
                )
            )
    return items[: project.count]
