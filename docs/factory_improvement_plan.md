# Factory Improvement Plan

Reference date: 2026-05-04 JST.

This plan records the next improvements needed to make the LINE sticker and emoji factory reliable across arbitrary user ideas, themes, and genres. It is based on the current v1 scope: ordinary static LINE stickers, regular LINE emoji, Python CLI operation, and manual LINE Creators Market upload.

Implementation note: the 2026-05-04 improvement pass implemented the P0 gate, sample fixture, metadata validation, ZIP re-validation, data-aware risk report, source mapping, source manifest warnings, and expanded visual QA. Remaining P2/P3 work can further tune false positives and package layout cleanup.

## Current Baseline

Verified locally:

- `python -m compileall scripts`: pass
- `pytest`: pass
- `python -m line_factory.cli --help`: pass

Known gaps:

- `projects/sample_static_sticker/` is referenced by `README.md` and `AGENTS.md`, but the sample project is missing.
- `package` can create a ZIP while all human approval gates are still pending.
- Opaque or bad source backgrounds can be converted into final files that pass transparency validation.
- Project metadata is not deeply validated against LINE text and review constraints.
- ZIP verification does not yet re-check dimensions, transparency, color mode, and image-level rules inside the archive.

Official LINE references checked on 2026-05-04 JST:

- Sticker Creation Guidelines: `https://creator.line.me/en/guideline/sticker/`
- Emoji Creation Guidelines: `https://creator.line.me/en/guideline/emoji/`
- Review Guidelines: `https://creator.line.me/en/review_guideline/`

## Goals

- Prevent the CLI from producing upload-ready artifacts when fatal validations are missing, and block missing approvals unless an explicit automated approval policy is active.
- Catch the most common generation and finishing failures before manual upload.
- Keep the project flow generic enough for any original theme, character, object, or genre.
- Make all quality gates reproducible through CLI reports and tests.
- Keep v1 conservative and avoid adding unsupported product types.

## Non-Goals

- Automated LINE Creators Market login, upload, pricing, or sales submission.
- Animated, custom, message, Big, pop-up, or effect stickers.
- Full legal review automation or guaranteed LINE approval.
- Replacing human visual QA for text accuracy, rights risk, or final taste decisions.

## P0: Block Unsafe Packaging

### 1. Enforce HAG State Before ZIP Creation

Problem: `package` currently blocks only fatal validation errors. It does not block missing HAG approvals.

Target behavior:

- `package` must fail when any of HAG-1 through HAG-5 is not approved in manual mode.
- `package` may proceed with pending HAG entries only when `automation.approval_policy: automated` is explicit in `project.yml`.
- `validate` should report approval status clearly.
- Approval state should be read from one canonical source, preferably `project.yml`, with `approvals.md` treated as human-readable notes.
- If a future override is needed, it must be explicit and visibly named, such as `--allow-unapproved-package`, and should not be used in production workflows.

Likely files:

- `scripts/line_factory/project.py`
- `scripts/line_factory/validate.py`
- `scripts/line_factory/package.py`
- `projects/_template/project.yml`
- `projects/_template/approvals.md`
- `tests/test_e2e.py`

Acceptance criteria:

- A freshly initialized manual project cannot be packaged.
- A project with validation errors cannot be packaged.
- A project with all required HAG approvals and valid final PNGs can be packaged.
- An automated-policy project with valid metadata and PNGs can be packaged without editing HAG entries.
- Validation output lists each gate as approved, pending, or automated.

### 2. Restore the Sample Project Contract

Problem: repository instructions require sample verification commands that fail because `projects/sample_static_sticker/` is missing.

Target behavior:

- Add a deterministic `projects/sample_static_sticker/` fixture, or change the documented verification flow to create a temporary sample project.
- Keep generated fixture art clearly labeled as test-only fallback art.
- Ensure the sample command sequence in `AGENTS.md` and `README.md` works as written.

Likely files:

- `projects/sample_static_sticker/`
- `README.md`
- `AGENTS.md`
- `.gitignore`
- `tests/test_e2e.py`

Acceptance criteria:

- `python -m line_factory.cli finish --project projects/sample_static_sticker` passes.
- `python -m line_factory.cli validate --project projects/sample_static_sticker` passes or fails only for deliberately documented approval status, depending on the final packaging policy.
- `python -m line_factory.cli package --project projects/sample_static_sticker` has a documented expected outcome under the HAG policy.

## P1: Strengthen Image Validation

### 3. Detect Opaque or Bad Source Backgrounds

Problem: an opaque RGB source can be centered onto a transparent final canvas and pass `has_transparency`, even if the artwork itself has an unremoved background.

Target behavior:

- Warn or fail when item artwork has large opaque rectangular coverage suggesting an unremoved background.
- Check corner alpha and edge alpha for final item images.
- Detect common chroma-key residue when configured, such as flat green or magenta edges.
- Report whether a source image was transparent before finishing when that information is available.

Likely files:

- `scripts/line_factory/images.py`
- `scripts/line_factory/finish.py`
- `scripts/line_factory/validate.py`
- `rules/quality_thresholds.yml`
- `tests/test_e2e.py`

Acceptance criteria:

- Fully opaque rectangular source images do not pass production validation silently.
- Proper transparent PNGs continue to pass.
- Warnings explain whether the risk is source transparency, final edge alpha, or suspected background residue.

### 4. Re-Validate ZIP Image Contents

Problem: ZIP verification checks names, size, and PNG signatures, but not the full image rules described in the README.

Target behavior:

- Re-open each PNG inside the ZIP and validate dimensions, transparency, color mode, and file size.
- Keep ZIP content order exactly matching LINE expectations.
- Surface ZIP validation failures as `PackageError`.

Likely files:

- `scripts/line_factory/package.py`
- `scripts/line_factory/validate.py`
- `tests/test_e2e.py`

Acceptance criteria:

- Tampered ZIP contents fail packaging verification.
- ZIP validation behavior matches the README wording.

### 5. Add Chat-Size Visual QA Previews

Problem: current contact sheets show final files, but do not simulate actual small chat readability.

Target behavior:

- Generate a visual report with transparent checkerboard, white background, dark background, and chat-size thumbnails.
- Show item filename, item text, and warning badges when available.
- Keep the original contact sheet for quick overview.

Likely files:

- `scripts/line_factory/contact_sheet.py`
- `scripts/line_factory/images.py`
- `scripts/line_factory/visual_report.py`
- `rules/quality_thresholds.yml`

Acceptance criteria:

- `report` creates visual artifacts that reveal low contrast, tiny text, crop issues, and background problems.
- Reports remain usable for both sticker and emoji projects.

## P1: Strengthen Metadata and Review Risk Checks

### 6. Validate LINE Metadata

Problem: `creator_name`, `title`, `description`, and `copyright` can be blank or over the official limits without fatal errors.

Target behavior:

- Validate required metadata fields before packaging.
- Enforce configured character limits.
- Warn on URLs, advertising phrases, extremely short text, unsupported emoji or device-dependent symbols, and obvious placeholder text.
- Record Asian-language character counting policy in rules and tests.

Likely files:

- `scripts/line_factory/validate.py`
- `rules/line_static_sticker.yml`
- `rules/line_static_emoji.yml`
- `rules/review_risk.yml`
- `rules/quality_thresholds.yml`
- `tests/test_e2e.py`

Acceptance criteria:

- Blank required metadata blocks packaging.
- Over-limit metadata blocks validation.
- URL and advertising-like metadata warnings appear in `reports/validation.md`.

### 7. Make Risk Report Data-Aware

Problem: `risk_report.md` is currently a static checklist. It does not inspect project files.

Target behavior:

- Scan `brief.md`, `items.csv`, and metadata for risk keywords.
- Flag rights, trademarks, existing IP, portraits, public figures, internet service references, messenger app references, religion, politics, medical claims, donations, gambling, sexual content, violence, discrimination, and illegal activity.
- Keep all findings as human-review aids, not approval guarantees.

Likely files:

- `scripts/line_factory/risk_report.py`
- `scripts/line_factory/reports.py`
- `rules/review_risk.yml`
- `tests/test_e2e.py`

Acceptance criteria:

- Risk report includes project-specific findings.
- Static checklist remains available.
- Findings are included in HAG-2 and HAG-5 review context.

## P2: Improve Production Traceability

### 8. Make Source-to-Item Mapping Explicit

Problem: `finish` maps source PNGs to items by sorted filename order. That is fragile for real production batches.

Target behavior:

- Add optional `source_file` to `items.csv`.
- If present, finish each item from its declared source file.
- If absent, require strict stable names such as `source_01.png`, `source_02.png`, or warn before using sorted fallback.
- Include mapping in `reports/validation.md`.

Likely files:

- `projects/_template/items.csv`
- `scripts/line_factory/project.py`
- `scripts/line_factory/generation.py`
- `scripts/line_factory/finish.py`
- `scripts/line_factory/validate.py`
- `tests/test_e2e.py`

Acceptance criteria:

- Swapped or missing source files are detected before finishing.
- Generation plan names match the expected source mapping.
- The final report can trace every final PNG back to its source PNG.

### 9. Preserve Raw Generation Evidence

Problem: the workflow recommends keeping accepted raw outputs under `assets/working/`, but the CLI does not help verify traceability.

Target behavior:

- Add a manifest file such as `assets/working/source_manifest.yml`.
- Record item index, source file, raw generation file, prompt/report reference, approval notes, and known exceptions.
- Surface missing manifest entries as warnings before HAG-5.

Likely files:

- `projects/_template/`
- `scripts/line_factory/generation.py`
- `scripts/line_factory/validate.py`
- `workflows/04_generate.md`

Acceptance criteria:

- Production projects can explain where each source image came from.
- Fallback-quality sources are clearly labeled and require human approval.

## P2: Clean Up Package Structure

### 10. Unify the Python Package Layout

Problem: the repo has a root `line_factory` compatibility wrapper and the real package under `scripts/line_factory`. CLI use works, but direct module imports can be confusing.

Target behavior:

- Prefer a conventional package layout, either `src/line_factory` or a single root `line_factory`.
- Keep `python -m line_factory.cli` stable.
- Remove the need for path-specific import knowledge in tests and maintenance scripts.

Likely files:

- `pyproject.toml`
- `line_factory/`
- `scripts/line_factory/`
- `tests/`

Acceptance criteria:

- `python -m line_factory.cli --help` works from a clean editable install.
- `python -c "from line_factory.specs import expected_images"` works.
- Existing tests pass without special import assumptions.

### 11. Guard Destructive Init Operations

Problem: `init --force` deletes the target path recursively.

Target behavior:

- Refuse to force-delete paths outside the intended workspace or `projects/` unless explicitly allowed.
- Print the resolved target path before destructive action.
- Keep non-interactive CLI behavior predictable.

Likely files:

- `scripts/line_factory/project.py`
- `tests/test_e2e.py`

Acceptance criteria:

- `init --force` works inside `projects/<name>`.
- Unsafe paths are refused with a clear error.

## P3: Expand Quality Intelligence

### 12. Add Contrast and Readability Checks

Problem: `warn_low_contrast_luma_delta` exists but is not used.

Target behavior:

- Estimate item contrast against light and dark chat backgrounds.
- Warn when visible content is too pale, too low contrast, or too fine-lined for emoji scale.
- Give stricter recommendations for regular emoji than static stickers.

Likely files:

- `scripts/line_factory/images.py`
- `scripts/line_factory/validate.py`
- `rules/quality_thresholds.yml`

Acceptance criteria:

- Low-contrast images trigger warnings.
- High-contrast images pass without false positives in common cases.

### 13. Improve Duplicate and Variety Detection

Problem: average hash catches only obvious similarity and may miss repeated poses or tiny changes.

Target behavior:

- Add optional perceptual checks for bbox size, dominant colors, silhouette similarity, and expression text repetition.
- Keep warnings human-review oriented.
- Avoid blocking legitimate style consistency.

Likely files:

- `scripts/line_factory/images.py`
- `scripts/line_factory/validate.py`
- `rules/quality_thresholds.yml`

Acceptance criteria:

- Near-identical items are flagged.
- Visually consistent but meaningfully different items do not produce excessive warnings.

### 14. Normalize Mojibake and Placeholder Checks

Problem: current mojibake tokens contain replacement-character artifacts and are hard to maintain.

Target behavior:

- Move suspect text patterns into a clean, documented list.
- Include placeholder terms such as `TBD`, `TODO`, `draft`, `sample`, and repeated punctuation.
- Test common malformed Japanese examples.

Likely files:

- `rules/quality_thresholds.yml`
- `scripts/line_factory/validate.py`
- `tests/test_e2e.py`

Acceptance criteria:

- Known malformed tokens are detected.
- Legitimate Japanese text is not warned by default.

## Workflow Updates

When the implementation work starts, update the workflow docs as each feature lands:

- `workflows/01_intake.md`: document metadata fields required before packaging.
- `workflows/03_style_lock.md`: require explicit background and edge-treatment policy.
- `workflows/04_generate.md`: require source manifest and source filename mapping.
- `workflows/06_validate.md`: describe approval, metadata, source, and visual QA checks.
- `workflows/07_package.md`: state that packaging is blocked by pending HAG approvals.

## Test Matrix

Add or update tests for:

- Pending HAG approvals block packaging in manual mode.
- Explicit automated approval policy allows packaging while HAG entries remain pending.
- Approved valid project packages successfully.
- Missing sample fixture commands match documentation.
- Opaque rectangular source images are flagged.
- Transparent source images pass.
- Metadata length and required fields are enforced.
- URL and advertising text warnings appear.
- ZIP tampering fails verification.
- Explicit `source_file` mapping works.
- Direct import of `line_factory.specs` works after package cleanup.

## Recommended Implementation Order

1. Restore sample project contract.
2. Enforce HAG state before packaging.
3. Add source/background transparency validation.
4. Add metadata validation.
5. Re-validate ZIP image contents.
6. Add data-aware risk report.
7. Add explicit source mapping and manifest.
8. Improve visual reports.
9. Clean up package layout.
10. Add contrast, duplicate, and mojibake refinements.

## Definition of Done

The improvement series is complete when:

- All documented verification commands pass.
- `package` cannot produce a production ZIP without passing validation, and requires either manual approvals or explicit automated approval policy.
- Reports give enough context for HAG-5 without inspecting raw folders manually.
- A new project can be taken from idea to manual upload preparation using only `projects/_template/`, workflows, rules, prompts, and CLI commands.
- Remaining manual responsibilities are explicit: final human approval, LINE upload, pricing, and sales submission.
