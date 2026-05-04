# Agent Operating Notes

## Scope

Build and operate a generic high-quality LINE sticker and LINE emoji production factory v1.

v1 supports:

- Ordinary static LINE stickers
- Regular LINE emoji
- Python CLI pipeline
- Codex built-in `image_gen` production artwork through the `imagegen` skill

v1 does not support:

- Animated stickers or emoji
- Custom, message, Big, pop-up, or effect stickers
- LINE Creators Market upload automation
- Price setting or sales submission automation
- Source-PNG fallback, Pillow-generated, simple-geometry, placeholder, or code-generated production artwork

## Required Project Flow

Use `projects/_template/` for new work. Source images go in `assets/source/`, intermediate files in `assets/working/`, final PNGs in `assets/final/`, reports in `reports/`, and ZIPs in `dist/`.

The public CLI shape is:

```powershell
python -m line_factory.cli <command> --project projects/<name>
```

Initial commands are `init`, `generate-plan`, `finish`, `validate`, `package`, and `report`.

## Approval Policy

Default projects use manual human approval gates. Stop and clearly request human approval at:

- HAG-1: concept, target users, use cases, count, language
- HAG-2: rights, trademarks, people, existing IP, advertising, prohibited motifs
- HAG-3: style lock from base candidates
- HAG-4: item list and expression/text balance before production
- HAG-5: final visual QA and review-risk check before ZIP upload

Approval state is canonical in `project.yml`; `approvals.md` is for human-readable notes.

Fully automated projects may set `automation.approval_policy: automated` in `project.yml` or be created with `python -m line_factory.cli init --approval-policy automated`. In automated mode, do not stop for HAG-1 through HAG-5; instead run automated validation, risk reporting, visual report generation, and packaging. Never mark a project READY if validation has fatal errors. In manual mode, also never mark READY if a required approval is missing.

Production sticker and emoji source artwork must be generated with Codex built-in `image_gen` through the `imagegen` skill. If built-in image generation is unavailable, stop production instead of substituting local Source-PNG fallback. Local fixture art is allowed only for `status: fixture` test projects such as `projects/sample_static_sticker`.

## Rights and Review Constraints

Avoid third-party trademarks, copyrighted work, existing characters, celebrity likenesses, fan art, unclear-rights materials, corporate-logo-only assets, advertising copy, political/religious solicitation, sexual content, graphic violence, discrimination, illegal activity, and public-order risks.

Do not use prompts such as "in the style of a famous work", "like a famous character", "in a specific living artist style", or "corporate logo style".

## Verification

Before declaring implementation complete, run:

```powershell
python -m compileall scripts
pytest
python -m line_factory.cli --help
python -m line_factory.cli finish --project projects/sample_static_sticker
python -m line_factory.cli validate --project projects/sample_static_sticker
python -m line_factory.cli package --project projects/sample_static_sticker
```

ZIP upload remains manual after HAG-5 in manual mode, or after successful automated validation/package in automated mode.

`projects/sample_static_sticker` is a test-only approved fixture so the verification commands can exercise packaging under HAG enforcement. Do not treat it as production artwork.
