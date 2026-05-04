# 06 Validate

Input: final PNGs and project metadata.

Command:

```powershell
python -m line_factory.cli validate --project projects/<name>
python -m line_factory.cli market-audit --project projects/<name>
```

Output: `reports/validation.md`, `reports/risk_report.md`, `reports/contact_sheet.png`, `reports/visual_report.png`, and `reports/market_quality.md`.

Fatal errors block READY status and packaging. Pending HAG approvals are fatal for packaging unless `project.yml` explicitly sets `automation.approval_policy: automated`. Warnings require review by the active approval policy.

Technical validation is not market readiness. A project may have valid PNGs and ZIPs while still failing character appeal, expression variety, text integration, current market fit, or communication clarity. `market-audit` must pass before a project is described as ready for manual upload.

Validation QA notes:

- In manual mode, confirm HAG-1 through HAG-5 are `approved` in `project.yml` only after real human review.
- In automated mode, confirm `automation.approval_policy: automated` is intentional and use validation, risk, contact-sheet, and visual reports as the gate evidence.
- Confirm required metadata fields pass length checks and contain no URLs, advertising-like wording, placeholders, or device-dependent symbols.
- Confirm every item has a traceable `source_file` in `items.csv`; review `reports/source_mapping.yml` after `finish`.
- Confirm `assets/working/source_manifest.yml` records raw-generation evidence or approved fallback-source notes.
- Review the data-aware findings in `reports/risk_report.md` during HAG-2 and HAG-5.
- Treat `???`, mojibake, malformed Japanese text, or duplicate tiny generated text as human-review blockers even when file-format validation passes.
- Review `reports/contact_sheet.png`, `reports/visual_report.png`, and `reports/generation_qa_checklist.md` before HAG-5.
- Confirm production artwork does not look like a physical sticker mockup unless that was explicitly approved in HAG-3.
- Confirm `reports/market_quality.md` passes. If it fails, keep the project in `needs_revision` even if `validate` passes.
