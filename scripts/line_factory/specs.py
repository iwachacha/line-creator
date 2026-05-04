from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = ROOT / "rules"


class SpecError(ValueError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise SpecError(f"YAML root must be a mapping: {path}")
    return data


def load_kind_spec(kind: str) -> dict[str, Any]:
    filename = {
        "static_sticker": "line_static_sticker.yml",
        "regular_emoji": "line_static_emoji.yml",
    }.get(kind)
    if not filename:
        raise SpecError(f"Unsupported project kind for v1: {kind}")
    return load_yaml(RULES_DIR / filename)


def load_quality_thresholds() -> dict[str, Any]:
    return load_yaml(RULES_DIR / "quality_thresholds.yml")


def load_review_risk() -> dict[str, Any]:
    return load_yaml(RULES_DIR / "review_risk.yml")


@dataclass(frozen=True)
class ExpectedImage:
    role: str
    filename: str
    width: int | None = None
    height: int | None = None
    max_width: int | None = None
    max_height: int | None = None
    required_alpha: bool = False
    even_dimensions: bool = False


def valid_count(kind: str, count: int, spec: dict[str, Any] | None = None) -> bool:
    spec = spec or load_kind_spec(kind)
    if kind == "static_sticker":
        return count in spec["images"]["stickers"]["counts"]
    if kind == "regular_emoji":
        counts = spec["images"]["emoji"]["counts"]
        return int(counts["min"]) <= count <= int(counts["max"])
    return False


def expected_images(kind: str, count: int, spec: dict[str, Any] | None = None) -> list[ExpectedImage]:
    spec = spec or load_kind_spec(kind)
    if not valid_count(kind, count, spec):
        raise SpecError(f"Invalid count for {kind}: {count}")
    images = spec["images"]
    fmt = spec["format"]
    required_alpha = bool(fmt.get("required_alpha_for_item_images", True))
    if kind == "static_sticker":
        result = [
            ExpectedImage("main", images["main"]["filename"], images["main"]["width"], images["main"]["height"]),
            ExpectedImage("tab", images["tab"]["filename"], images["tab"]["width"], images["tab"]["height"]),
        ]
        sticker = images["stickers"]
        for index in range(1, count + 1):
            result.append(
                ExpectedImage(
                    "item",
                    sticker["filename_pattern"].format(index=index),
                    max_width=sticker["max_width"],
                    max_height=sticker["max_height"],
                    required_alpha=required_alpha,
                    even_dimensions=bool(sticker.get("even_dimensions", False)),
                )
            )
        return result
    if kind == "regular_emoji":
        result = [ExpectedImage("tab", images["tab"]["filename"], images["tab"]["width"], images["tab"]["height"])]
        emoji = images["emoji"]
        for index in range(1, count + 1):
            result.append(
                ExpectedImage(
                    "item",
                    emoji["filename_pattern"].format(index=index),
                    emoji["width"],
                    emoji["height"],
                    required_alpha=required_alpha,
                )
            )
        return result
    raise SpecError(f"Unsupported project kind for v1: {kind}")
