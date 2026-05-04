# Production Trial: soft_work_mochi

Reference date: 2026-05-04 JST.

## Trial Scope

Goal: run one sticker pack from market research through project setup, planning, source PNG production, finish, validate, market audit, reports, and ZIP packaging.

Project: `projects/soft_work_mochi`

Output ZIP from the original trial: `projects/soft_work_mochi/dist/soft_work_mochi_line_stickers.zip`

Status update: this ZIP is now explicitly not upload-ready. The source artwork was produced by local Source-PNG fallback during the trial, and the factory has since been corrected to reject that method for production projects.

## Market Strategy Used

Product concept: `まるもち敬語メモ`

Buyer reason: work-safe and family-safe polite stickers for high-friction chat moments: acknowledgement, gratitude, waiting, checking, relief, effort recognition, no-pressure permission, and soft closing.

Differentiation:

- Not a generic cute pack; it solves "角を立てない小さな気づかい".
- Uses one original rounded sticky-note/mochi mascot rather than an existing animal/IP trope.
- Phrases are high-frequency and polite, with emotional acting to justify using a sticker instead of plain text.

Market references:

- LINE sticker creation guidelines require PNG, transparent backgrounds, correct sizes, daily-use communication fit, visibility, and variety: https://creator.line.me/en/guideline/sticker/
- LINE review guidelines warn against poor daily usefulness, poor visibility, low variety, text-only images, spelling mistakes, advertising/URLs, other messenger references, unclear rights, public figures, fan art, and trademark/copyright issues: https://creator.line.me/en/review_guideline/
- Marketplace/community observation still points toward cute everyday emotions, work fatigue, gratitude, and relatable daily reactions as durable demand areas.

## Factory Results

- `init`: pass with `automation.approval_policy: automated`
- `generate-plan`: pass
- `finish`: pass
- `validate`: originally passed; now correctly fails because production art did not come from Codex built-in `image_gen`
- `market-audit`: originally passed after factory fixes; now correctly fails because production art used Source-PNG fallback
- `report`: pass after factory fixes
- `package`: pass

Created reports:

- `reports/market_research_notes.md`
- `reports/character_design_lock.md`
- `reports/item_communication_plan.md`
- `reports/contact_sheet.png`
- `reports/visual_report.png`
- `reports/chat_size_preview.png`
- `reports/validation.md`
- `reports/market_quality.md`
- `reports/risk_report.md`

## Fixes Applied During Trial

1. Production image creation incorrectly used local Source-PNG fallback instead of Codex built-in `image_gen`.
   - Fix: `scripts/line_factory/validate.py` now treats fallback, Pillow, placeholder, fixture, simple-geometry, or code-generated production source methods as fatal for non-fixture projects.
   - Fix: `scripts/line_factory/market_quality.py` now fails market audit when source evidence indicates fallback production art.
   - Fix: `AGENTS.md` and `rules/generation_quality.md` now state that production sticker/emoji artwork must use Codex built-in `image_gen` through the `imagegen` skill.

2. `reports/chat_size_preview.png` was required by `rules/sticker_market_quality.yml`, but the report generator did not create it.
   - Fix: `scripts/line_factory/visual_report.py` now creates `chat_size_preview.png` and references it in `visual_report.md`.

3. Market-quality variety scoring falsely failed because every item description began with the same structured label text.
   - Fix: `scripts/line_factory/market_quality.py` now normalizes common labels before estimating item variety.

## Gaps Found

### P0: Visual Text Accuracy Is Not Machine-Gated

The first generated source images rendered Japanese text as `????`. Technical validation passed and market audit initially only failed for unrelated artifact/variety reasons.

Impact: a pack can become technically valid while the actual sticker text is unusable.

Needed:

- Add an OCR-assisted visual text QA step, or at least an automated image-text anomaly detector for repeated `?`, tofu boxes, mojibake, and missing kana/kanji.
- Make HAG-5 checklist explicitly compare `items.csv` text against `contact_sheet.png` and `chat_size_preview.png`.
- Add a warning when project text contains Japanese but generated visual previews contain no detectable Japanese-like glyph density.

### P0: Market Audit Could Pass Prototype/Fallback Art Too Easily

After the documentation artifacts existed, the fallback prototype originally scored 100/100. That was wrong. The factory now fails non-fixture projects when source evidence indicates Pillow, Source-PNG fallback, placeholder, fixture, or other code-generated production art.

Impact: the market audit currently proves that planning artifacts exist more than it proves visual desirability.

Remaining needed:

- Add human-visible score notes for style polish, character charm, text craft, and thumbnail appeal.
- Add OCR or visual text checks so image-generated Japanese can be compared against `items.csv`.

### P1: `finish` And `report` Are Not Safe To Run Concurrently

Running `finish` and `report` at the same time caused `report` to fail because `finish` clears and rewrites `assets/final`.

Impact: parallel factory runs or UI-driven automation can produce intermittent failures.

Needed:

- Make `finish` write into a temporary final directory and atomically swap it into place.
- Add a project lock file around commands that mutate or read `assets/final`, `reports`, or `dist`.

### P1: Package Creation Is Still Technical-Only

`package` prints that users should run `market-audit`, but the command itself only blocks fatal technical validation errors. A workflow can still create a ZIP before market readiness is confirmed.

Impact: operators may mistake a ZIP for upload readiness.

Needed:

- Add `ready` or `pre-submit` command that requires validation, risk report, visual report, market audit, and approval state.
- Consider making `package` write a clear `NOT_READY_FOR_UPLOAD.txt` report when market audit has not passed.

### P2: Strategy Is Manual Markdown, Not A First-Class Schema

Market research, character lock, and item communication plan are currently free-form markdown. The audit only checks for words and files.

Impact: large-scale production will drift; prompts cannot reliably consume structured strategy.

Needed:

- Add `strategy.yml` with fields for buyer promise, target contexts, visual hook, phrase roles, risk exclusions, and production method.
- Generate prompts, audit checks, and reports from this schema.

## Human HAG-5 Notes For This Trial

Use these files for the joint final review:

- `projects/soft_work_mochi/reports/contact_sheet.png`
- `projects/soft_work_mochi/reports/chat_size_preview.png`
- `projects/soft_work_mochi/reports/visual_report.png`

Known review focus:

- Long phrases are readable in the contact sheet, but still small in chat-size preview.
- Source-PNG fallback art is now rejected for production, regardless of visual coherence.
- The concept and item mix can be reused. For sale-level production, regenerate all source artwork with Codex built-in `image_gen` through the `imagegen` skill while preserving this strategy.
