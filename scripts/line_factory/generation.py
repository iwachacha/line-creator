from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .project import Project, load_items


@dataclass(frozen=True)
class GenerationItem:
    index: int
    text: str
    description: str


def load_generation_items(project: Project) -> list[GenerationItem]:
    return [GenerationItem(item.index, item.text, item.description) for item in load_items(project)]


def build_image_generation_plan(project: Project) -> str:
    items = load_generation_items(project)
    if len(items) < project.count:
        raise RuntimeError(f"Need {project.count} item rows in items.csv, found {len(items)}")

    product = "ordinary static LINE sticker" if project.kind == "static_sticker" else "regular LINE emoji"
    target_size = "370 x 320 px final sticker canvas" if project.kind == "static_sticker" else "180 x 180 px final emoji canvas"
    source_note = (
        "Generate each source as a high-resolution square or near-square PNG-ready illustration with generous padding. "
        "The CLI will resize and center it for LINE's final dimensions."
    )
    approval_note = (
        "Automated approval policy is active; proceed through generation, QA, validate, and package without HAG stops."
        if project.uses_automated_approvals
        else "Manual approval policy is active; stop at required HAG checkpoints."
    )
    final_step = (
        "7. Continue to `python -m line_factory.cli package --project <project>` after automated QA passes."
        if project.uses_automated_approvals
        else "7. Stop for HAG-5 before ZIP upload."
    )

    lines = [
        f"# Image Generation Plan: {project.name}",
        "",
        "This plan is for Codex operation. The local Python CLI cannot call the built-in image generation tool directly.",
        "Use the Codex built-in `image_gen` tool for production artwork, then copy the selected outputs into `assets/source/`.",
        "",
        "## Market-Grade Prerequisites",
        "- Technical validation is not market readiness. Before production, create `reports/market_research_notes.md`, `reports/character_design_lock.md`, and `reports/item_communication_plan.md`.",
        "- Lock a memorable character first: silhouette, face, expression range, signature visual hook, and text system.",
        "- Each item plan must define chat function, emotional state, visual action, camera distance, and how the meaning reads without text.",
        "- Use rough 4x2 sheets only for ideation. Final adopted sticker sources should normally be generated or art-directed one item at a time.",
        "- After production, run `python -m line_factory.cli market-audit --project <project>` and do not treat a project as upload-ready if it fails.",
        "",
        "## Required Generation Mode",
        "- Use the built-in `image_gen` tool through the Codex `imagegen` skill.",
        "- Do not create production source art with Pillow, simple shapes, placeholder SVGs, dummy fallback images, or other code-generated art.",
        "- If built-in image generation is unavailable, stop. Production sticker/emoji artwork must not silently downgrade to Source-PNG fallback.",
        "- Keep all artwork original: no existing characters, famous work styles, living artist styles, logos, trademarks, or public figures.",
        "- For transparent final assets, generate with Codex built-in `image_gen` on a flat chroma-key background and remove it locally, or use an explicitly approved native-transparency image-generation path.",
        "- When sticker text is part of the concept, generate the text inside the artwork. Do not default to a separate post-processing label or generic speech bubble.",
        "- Generate artwork for LINE usage, not for physical sticker mockups. Avoid die-cut borders, paper backing, drop shadows, sticker-sheet presentation, and decorative frames unless explicitly style-locked.",
        "",
        "## Shared Prompt Frame",
        f"Use case: illustration-story",
        f"Asset type: {product}",
        f"Project: {project.name}",
        f"Approval policy: {project.approval_policy}",
        approval_note,
        f"Final target: {target_size}",
        f"Language: {project.config.get('language', 'ja')}",
        f"Source handling: {source_note}",
        "Style/medium: high-quality polished digital sticker illustration, crisp edges, clean silhouette, expressive character acting, readable at chat size",
        "Composition/framing: centered full-body or bust sticker pose, clear chat-size silhouette, no crop, generous safe padding, no physical-sticker mockup treatment",
        "Background: flat removable chroma-key color only if transparency post-processing is needed; otherwise transparent PNG-ready",
        "Typography: integrate approved text as hand-painted lettering that matches the sticker world, with the exact phrase shown once, large enough for chat-size readability",
        "Avoid: logos, watermarks, photo realism, existing IP, famous character resemblance, famous artwork style, specific living artist style, advertising copy, cluttered backgrounds",
        "",
        "## Integrated Text Protocol",
        "- Prefer image-generation-native text for production sticker wording.",
        "- Prompt the exact text as `Text must read exactly: \"...\"` and describe how it belongs to the scene, such as steam, motion marks, cheering lettering, or hand-painted accents.",
        "- Keep text short, large, and high contrast; ask for one phrase only and avoid duplicate tiny copies.",
        "- Avoid generic rectangular labels unless the approved style specifically uses them.",
        "- If generated Japanese text is wrong, regenerate that item with stronger text constraints. Do not replace production artwork with local code-generated text art.",
        "- Record accepted raw outputs under `assets/working/` and keep `assets/working/source_manifest.yml` current so HAG-5 can trace the selected generation.",
        "",
        "## Raw Generation QA",
        "- Inspect raw generated images before `finish`; a contact sheet is recommended for batches.",
        "- Check exact text, typos, mojibake, duplicated tiny text, style drift, physical sticker artifacts, rights risk, expression variety, and transparent-background readiness.",
        "- Copy only accepted generated images into `assets/source/`.",
        "",
        "## Item Prompts",
    ]
    for item in items:
        text_part = (
            f'Text (verbatim): "{item.text}"'
            if item.text
            else "Text: no text unless allowed by the approved item plan or automated production plan"
        )
        filename = f"{item.index:02d}.png" if project.kind == "static_sticker" else f"{item.index:03d}.png"
        lines.extend(
            [
                "",
                f"### Source {item.index:02d} -> {filename}",
                f"Primary request: {item.description or f'Item {item.index}'}",
                text_part,
                "Constraints: match the approved style lock exactly; integrate any approved text into the illustration itself; avoid physical sticker mockup artifacts; vary pose, emotion, props, and silhouette from the other items; keep the character original and rights-safe.",
            ]
        )
    lines.extend(
        [
            "",
            "## After Generation",
            "1. Inspect each generated image for quality, rights risk, text accuracy, and expression variety.",
            "2. Regenerate malformed Japanese text before considering local text compositing.",
            "3. Copy accepted images into `assets/source/` using the `source_file` names declared in `items.csv`, such as `source_01.png`.",
            "4. Record source mapping and raw-generation evidence in `assets/working/source_manifest.yml`.",
            "5. Run `python -m line_factory.cli finish --project <project>`.",
            "6. Run `python -m line_factory.cli validate --project <project>` and review warnings.",
            final_step,
        ]
    )
    return "\n".join(lines) + "\n"


def write_image_generation_plan(project: Project) -> Path:
    project.reports_dir.mkdir(parents=True, exist_ok=True)
    output = project.reports_dir / "image_generation_plan.md"
    output.write_text(build_image_generation_plan(project), encoding="utf-8")
    return output


def build_generation_qa_checklist(project: Project) -> str:
    final_qa_line = (
        "- [ ] Automated final QA has reviewed `reports/contact_sheet.png` and `reports/visual_report.png` before packaging."
        if project.uses_automated_approvals
        else "- [ ] HAG-5 will review final `reports/contact_sheet.png` before manual upload."
    )
    lines = [
        f"# Generation QA Checklist: {project.name}",
        "",
        "Use this checklist after image generation and before `finish` whenever production art is generated.",
        "",
        "## Source Artwork",
        "- [ ] Production art was generated with Codex built-in `image_gen` through the `imagegen` skill.",
        "- [ ] No Pillow, simple geometry, placeholder SVG, code-generated fallback, or dummy fixture art is being used as production artwork.",
        "- [ ] Accepted raw generation files are retained under `assets/working/` when practical.",
        "- [ ] Only accepted PNGs were copied into `assets/source/`.",
        "",
        "## Text Integration",
        "- [ ] Sticker text is integrated into the artwork when text is part of the concept.",
        "- [ ] Text is not merely a detached generic label or rectangular speech bubble unless style-locked.",
        "- [ ] Every phrase appears once, is readable at chat size, and matches `items.csv` exactly.",
        "- [ ] No `???`, mojibake, malformed kana/kanji, duplicate tiny text, or typo is visible.",
        "",
        "## LINE Fit",
        "- [ ] Artwork reads as LINE sticker or emoji art, not a physical sticker mockup.",
        "- [ ] No unwanted die-cut border, paper backing, drop shadow, sticker-sheet presentation, floor shadow, or frame remains.",
        "- [ ] Poses, expressions, silhouettes, and props are varied across the set.",
        "- [ ] Transparent-background or chroma-key removal path is ready before `finish`.",
        "",
        "## Rights and Review",
        "- [ ] No existing characters, famous work styles, specific living artist styles, logos, trademarks, public figures, advertising, or unclear-rights motifs.",
        final_qa_line,
        "",
    ]
    return "\n".join(lines)


def write_generation_qa_checklist(project: Project) -> Path:
    project.reports_dir.mkdir(parents=True, exist_ok=True)
    output = project.reports_dir / "generation_qa_checklist.md"
    output.write_text(build_generation_qa_checklist(project), encoding="utf-8")
    return output
