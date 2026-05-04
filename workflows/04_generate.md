# 04 Generate

Input: approved or automated style lock and item list.

Output: source PNGs in `assets/source/`.

Before production, confirm HAG-4 in manual mode. In automated mode, record the item-list, expression, wording, and balance rationale, then proceed.

Market-grade prerequisites:

- Create `reports/market_research_notes.md` with current LINE Store or Creators Market observations, buyer promise, and overused patterns to avoid.
- Create `reports/character_design_lock.md` before final item generation.
- Create `reports/item_communication_plan.md`. Each item must include phrase, chat function, emotional state, visual action, camera distance, difference from neighboring items, and how the meaning reads without text.
- Treat rough 4x2 generated sheets as ideation only. Final adopted item sources should normally be generated or art-directed one by one.

Required generation mode:

- Use the Codex built-in `image_gen` tool through the `imagegen` skill for production artwork.
- Run `python -m line_factory.cli generate-plan --project projects/<name>` to create `reports/image_generation_plan.md`.
- Generate each approved or automated-plan item with a dedicated prompt from that plan.
- Copy accepted generated images into `assets/source/` using the `source_file` names declared in `items.csv`, for example `source_01.png`.
- Record raw-output evidence, prompt references, source filenames, approval notes, and known exceptions in `assets/working/source_manifest.yml`.
- Do not use Pillow, simple geometry, placeholder SVGs, or dummy source PNGs as production artwork unless the user explicitly approves fallback quality.
- If built-in image generation is unavailable, stop and ask for human direction instead of silently downgrading.
- Generate artwork for LINE usage, not for a physical sticker mockup. Avoid unwanted die-cut white borders, paper backing, drop shadows, sticker-sheet presentation, floor shadows, or frames.

Integrated text rules:

- If text is part of the sticker concept, generate the text with the artwork instead of adding a generic post-processing label.
- Prompt exact wording as `Text must read exactly: "<phrase>"`.
- Describe the text as part of the world: hand-painted lettering, steam, motion marks, cheering marks, heart accents, or other style-locked elements.
- Keep phrases short, high-contrast, and large enough for chat-size readability.
- If Japanese text is malformed, regenerate that item with stricter text constraints before using a local text-compositing fallback.
- A generic detached label or caption box is not production quality unless explicitly justified in the style lock.

Generation QA:

- Use `reports/generation_qa_checklist.md` after generation and before `finish`.
- Retain accepted raw outputs under `assets/working/` when practical and keep the source manifest aligned with `items.csv`.
- Check exact text, typos, mojibake, duplicated tiny text, style drift, physical sticker artifacts, rights risk, expression variety, and transparent-background readiness.
- Run `python -m line_factory.cli market-audit --project projects/<name>` after production and do not treat a technically valid ZIP as market-ready if the market audit fails.

Prompting constraints: original characters only, no famous work style, no famous character style, no specific living artist style, no corporate logo style, no advertising or prohibited motifs.
