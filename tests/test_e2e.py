from pathlib import Path

import pytest
import yaml
from PIL import Image, ImageDraw

from line_factory.finish import finish_project
from line_factory.generation import build_generation_qa_checklist, build_image_generation_plan, write_generation_qa_checklist, write_image_generation_plan
from line_factory.market_quality import audit_market_quality, build_market_quality_report
from line_factory.package import PackageError, package_project, verify_zip, zip_listing
from line_factory.project import init_project, load_project
from line_factory.risk_report import build_risk_report
from line_factory.validate import validate_project
from line_factory.visual_report import build_visual_report


def make_sources(project_path: Path, count: int) -> None:
    source = project_path / "assets" / "source"
    source.mkdir(parents=True, exist_ok=True)
    for i in range(1, count + 1):
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        color = (20 + i * 20, 80, 180, 255)
        draw.ellipse((36, 32, 220, 216), fill=color)
        draw.rectangle((78, 84, 104, 112), fill=(255, 255, 255, 255))
        draw.rectangle((152, 84, 178, 112), fill=(255, 255, 255, 255))
        draw.arc((86, 110, 170, 176), 0, 180, fill=(255, 255, 255, 255), width=8)
        img.save(source / f"source_{i:02d}.png")


def approve_project(project_path: Path) -> None:
    cfg_path = project_path / "project.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg.update(
        {
            "creator_name": "Factory Test",
            "title": "Factory Fixture",
            "description": "Fixture metadata for local validation tests.",
            "copyright": "(C) Factory Test",
            "approvals": {f"HAG-{i}": "approved" for i in range(1, 6)},
        }
    )
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    manifest = project_path / "assets" / "working" / "source_manifest.yml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        yaml.safe_dump(
            {
                "items": [
                    {
                        "index": i,
                        "source_file": f"source_{i:02d}.png",
                        "method": "Codex built-in image_gen via imagegen skill",
                        "identity_reference": "reports/character_consistency_qa.md model sheet",
                        "consistency_notes": "matches model sheet identity anchors",
                        "raw_generation_file": f"assets/working/image_gen_source_{i:02d}.png",
                        "prompt_reference": "reports/image_generation_plan.md",
                    }
                    for i in range(1, 9)
                ]
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def test_static_sticker_finish_validate_package(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert result.errors == []
    zip_path = package_project(project)
    assert zip_path.exists()
    assert zip_listing(zip_path) == ["main.png", "tab.png", "01.png", "02.png", "03.png", "04.png", "05.png", "06.png", "07.png", "08.png"]


def test_validate_reports_missing_files(tmp_path):
    project_path = tmp_path / "bad"
    init_project(project_path, "regular_emoji", 8)
    approve_project(project_path)
    project = load_project(project_path)
    result = validate_project(project)
    assert result.errors
    assert any("Missing required file" in e for e in result.errors)


def test_generate_plan_requires_builtin_imagegen(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    project = load_project(project_path)
    text = build_image_generation_plan(project)
    assert "built-in `image_gen` tool" in text
    assert "Do not create production source art with Pillow" in text
    assert "must not silently downgrade to Source-PNG fallback" in text
    assert "Integrated Text Protocol" in text
    assert "physical sticker mockups" in text
    assert "Market-Grade Prerequisites" in text
    assert "character_consistency_qa.md" in text
    assert "Character identity contract" in text
    assert "market-audit" in text
    plan_path = write_image_generation_plan(project)
    assert plan_path.exists()
    qa_text = build_generation_qa_checklist(project)
    assert "Character Consistency" in qa_text
    assert "No `???`, mojibake" in qa_text
    qa_path = write_generation_qa_checklist(project)
    assert qa_path.exists()


def test_validate_warns_on_suspect_project_text(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    make_sources(project_path, 8)
    items = project_path / "items.csv"
    items.write_text(items.read_text(encoding="utf-8") + "9,item,???,suspect,draft\n", encoding="utf-8")
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert any("suspect text token" in warning for warning in result.warnings)


def test_pending_hag_blocks_package(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert any("HAG-1" in error for error in result.errors)
    with pytest.raises(PackageError):
        package_project(project)


def test_automated_approval_policy_allows_package_without_hag_updates(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    cfg_path = project_path / "project.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["approvals"] = {f"HAG-{i}": "pending" for i in range(1, 6)}
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert not any("approval pending" in error for error in result.errors)
    assert any("approval policy: automated" in info for info in result.info)
    zip_path = package_project(project)
    assert zip_path.exists()


def test_invalid_approval_policy_fails_validation(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    cfg_path = project_path / "project.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["automation"] = {"approval_policy": "robot"}
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert any("automation.approval_policy" in error for error in result.errors)


def test_metadata_required_and_limited(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    cfg_path = project_path / "project.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["title"] = "x" * 41
    cfg["description"] = ""
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert any("metadata.title" in error and "exceeds" in error for error in result.errors)
    assert any("metadata.description" in error and "blank" in error for error in result.errors)


def test_opaque_source_warns(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    source = project_path / "assets" / "source"
    source.mkdir(parents=True, exist_ok=True)
    for i in range(1, 9):
        img = Image.new("RGB", (256, 256), (0, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((52, 52, 204, 204), fill=(30, 120, 220))
        img.save(source / f"source_{i:02d}.png")
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert any("source image has no transparency" in warning for warning in result.warnings)
    assert any("rectangular" in warning for warning in result.warnings)


def test_production_source_png_fallback_is_fatal(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    make_sources(project_path, 8)
    manifest = project_path / "assets" / "working" / "source_manifest.yml"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    for entry in data["items"]:
        entry["method"] = "Pillow vector-style transparent PNG source fallback"
    manifest.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert any("production source method is not allowed" in error for error in result.errors)
    with pytest.raises(PackageError):
        package_project(project)


def test_fixture_project_allows_local_test_art(tmp_path):
    project_path = tmp_path / "fixture"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    cfg_path = project_path / "project.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["status"] = "fixture"
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    make_sources(project_path, 8)
    manifest = project_path / "assets" / "working" / "source_manifest.yml"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    for entry in data["items"]:
        entry["method"] = "Pillow local fixture art"
    manifest.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    project = load_project(project_path)
    finish_project(project)
    result = validate_project(project)
    assert not any("production source method is not allowed" in error for error in result.errors)
    assert any("fixture project" in info for info in result.info)


def test_zip_tampering_fails_verification(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    zip_path = package_project(project)
    with zip_path.open("r+b") as f:
        data = f.read()
        f.seek(0)
        f.write(data.replace(b"\x89PNG\r\n\x1a\n", b"NOTAPNG!", 1))
        f.truncate()
    with pytest.raises(PackageError):
        verify_zip(project, zip_path)


def test_risk_report_is_data_aware(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8)
    approve_project(project_path)
    (project_path / "brief.md").write_text("A campaign sticker with a logo reference.", encoding="utf-8")
    project = load_project(project_path)
    text = build_risk_report(project)
    assert "campaign" in text
    assert "logo" in text


def write_market_quality_artifacts(project_path: Path) -> None:
    reports = project_path / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "market_research_notes.md").write_text(
        "Current LINE Store market observations: buyer demand, ranking patterns, daily use, cute replies.",
        encoding="utf-8",
    )
    (reports / "character_design_lock.md").write_text(
        "Character design lock: memorable silhouette, face, expression range, mascot identity, signature hook, identity anchors, model sheet, fixed proportions.",
        encoding="utf-8",
    )
    (reports / "character_consistency_qa.md").write_text(
        "Character consistency QA: model sheet, identity anchors, fixed proportions, same character, immutable face spacing and palette.",
        encoding="utf-8",
    )
    (reports / "item_communication_plan.md").write_text(
        "Each item records chat function, emotional state, camera distance, communication intent, and meaning without text.",
        encoding="utf-8",
    )
    Image.new("RGB", (320, 240), "white").save(reports / "chat_size_preview.png")


def write_structured_item_descriptions(project_path: Path) -> None:
    rows = [
        ("了解です", "checkmark memo; confident upright pose"),
        ("ありがとうございます", "deep bow and sparkle; formal warmth"),
        ("少しお待ちください", "clock and pause note; apologetic wait"),
        ("確認します", "checklist and magnifier; focused checking"),
        ("助かります", "hugging memo; relieved appreciation"),
        ("おつかれさまです", "warm cup; gentle recognition"),
        ("無理なくでOKです", "open hands; no-pressure permission"),
        ("また明日", "wave and moon memo; soft closing"),
    ]
    lines = ["index,type,text,description,status,source_file"]
    for i, (text, unique) in enumerate(rows, start=1):
        description = (
            "chat function: daily message; emotional state: polite; visual action: "
            + unique
            + "; camera: bust-up; meaning without text: clear; differs by unique pose"
        )
        lines.append(f'{i},item,{text},"{description}",approved,source_{i:02d}.png')
    (project_path / "items.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_market_quality_fails_without_market_artifacts(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = audit_market_quality(project)
    assert not result.ok
    assert any("required market-grade artifacts" in failure for failure in result.failures)
    report = build_market_quality_report(project, result)
    assert "Status: FAIL" in report


def test_market_quality_passes_with_character_and_market_artifacts(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    write_market_quality_artifacts(project_path)
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = audit_market_quality(project)
    assert result.ok
    assert result.total_score >= 80
    report = build_market_quality_report(project, result)
    assert "Status: PASS" in report


def test_market_quality_requires_character_consistency_qa(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    write_market_quality_artifacts(project_path)
    (project_path / "reports" / "character_consistency_qa.md").unlink()
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = audit_market_quality(project)
    assert not result.ok
    assert result.scores["style_consistency"] < 7
    assert any("character consistency QA" in finding for finding in result.findings)


def test_market_quality_fails_recorded_identity_drift(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    write_market_quality_artifacts(project_path)
    manifest = project_path / "assets" / "working" / "source_manifest.yml"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    data["items"][0]["consistency_notes"] = "identity drift: face spacing makes this read as a different character"
    manifest.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = audit_market_quality(project)
    assert not result.ok
    assert result.scores["style_consistency"] < 5
    assert any("character identity" in failure.lower() for failure in result.failures)


def test_visual_report_creates_required_chat_size_preview(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    build_visual_report(project)
    assert (project_path / "reports" / "chat_size_preview.png").exists()


def test_market_quality_variety_ignores_repeated_structured_labels(tmp_path):
    project_path = tmp_path / "case"
    init_project(project_path, "static_sticker", 8, approval_policy="automated")
    approve_project(project_path)
    write_market_quality_artifacts(project_path)
    write_structured_item_descriptions(project_path)
    make_sources(project_path, 8)
    project = load_project(project_path)
    finish_project(project)
    result = audit_market_quality(project)
    assert result.ok
    assert result.scores["expression_variety"] >= 7
