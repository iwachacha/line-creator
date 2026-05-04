# LINE Creator Factory Skill

Use this skill to operate the repository's LINE static sticker and regular emoji factory.

## Scope

Supported v1 products:

- Ordinary static LINE stickers
- Regular LINE emoji

Unsupported v1 products:

- Animated stickers or emoji
- Custom, message, Big, pop-up, or effect stickers
- Automated LINE Creators Market upload, pricing, or sales submission

## Standard Flow

1. Read `project.yml`, `brief.md`, `items.csv`, `approvals.md`, and rules under `rules/`.
2. Follow `workflows/01_intake.md` through `workflows/07_package.md`.
3. In manual mode, stop at HAG-1 through HAG-5 until human approval is recorded in `project.yml`; use `approvals.md` for human-readable notes. In automated mode, proceed without stopping when `project.yml` contains `automation.approval_policy: automated`, and record automated QA rationale in `approvals.md`.
4. Before production artwork, read `rules/sticker_market_quality.yml` and create or update market-grade notes: current market observations, character design lock, item communication plan, and market-quality risks.
5. For production artwork, use the Codex built-in `image_gen` tool through the `imagegen` skill. Generate one source image per approved item, inspect it, then copy accepted PNGs into `assets/source/`.
6. Use `python -m line_factory.cli generate-plan --project projects/<name>` before production to write `reports/image_generation_plan.md`.
7. Generate approved sticker text inside the artwork when text is part of the concept. Do not default to generic post-processing labels or detached speech bubbles.
8. Record negative style constraints, especially whether physical sticker artifacts are forbidden: die-cut borders, paper backing, drop shadows, sticker-sheet mockups, floor shadows, and frames.
9. Use `reports/generation_qa_checklist.md` to review raw generation quality before `finish` when production images are generated.
10. Keep each item's `source_file` mapping in `items.csv` and record raw source evidence in `assets/working/source_manifest.yml`.
11. Do not silently use Pillow, simple geometry, placeholder SVGs, or dummy fallback images for production artwork. If built-in image generation is unavailable, stop and ask for human direction.

## Market-Grade Quality Rules

Technical validation is not the same as sellable quality. A project that passes `validate` can still be below current LINE sticker market quality.

Before treating a project as ready for manual upload, check:

- Character appeal: memorable silhouette, face, identity, and repeatable charm.
- Communication clarity: the intent is understandable from the illustration, not only from text.
- Expression variety: face, pose, emotion, camera distance, and props vary meaningfully.
- Text integration: wording is readable and designed into the sticker world; generic detached label boxes are a failure unless explicitly style-locked.
- Current market fit: the pack does not look like old clip art, fixtures, or low-effort free stickers.
- Pack strategy: one-phrase packs still provide distinct emotional/use-case nuances.

Do not mark a project READY when market-grade quality fails, even in automated approval mode. Use `needs_revision` or equivalent wording and document the failure in reports.

Avoid using one 4x2 generated sheet as final production art. Sheet generation is acceptable for ideation, but final adopted items should normally be generated or art-directed one by one.

## CLI

```powershell
python -m line_factory.cli init --project projects/<name> --kind static_sticker --count 8
python -m line_factory.cli init --project projects/<name> --kind static_sticker --count 8 --approval-policy automated
python -m line_factory.cli generate-plan --project projects/<name>
python -m line_factory.cli finish --project projects/<name>
python -m line_factory.cli validate --project projects/<name>
python -m line_factory.cli package --project projects/<name>
python -m line_factory.cli report --project projects/<name>
```

## Readiness Rules

Never mark a project READY when validation has fatal errors. In manual mode, pending approvals also block readiness. In automated mode, pending HAG entries are allowed only when `automation.approval_policy: automated` is explicit and reports record the automated QA basis.

ZIP creation prepares manual upload assets only. The user must perform final visual confirmation, LINE Creators Market upload, pricing, and sales submission.

## Maintenance Notes

Before changing approval gates, validation, packaging, visual QA, source traceability, or workflow policy, read `docs/factory_improvement_plan.md` and keep the documented acceptance criteria in sync with the implementation.
