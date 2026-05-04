# 07 Package

Input: validated final PNGs, generated reports, and either HAG-5 approval or explicit automated approval policy.

Command:

```powershell
python -m line_factory.cli package --project projects/<name>
```

Output: `dist/<project>_line_stickers.zip` or `dist/<project>_line_emoji.zip`.

The CLI refuses packaging when validation has fatal errors. In manual mode, any pending HAG-1 through HAG-5 approval is a fatal validation error. In automated mode, `automation.approval_policy: automated` waives HAG blocking and packaging relies on automated validation and generated QA reports.

After writing the ZIP, the CLI re-opens every PNG inside the archive and verifies expected order, filename, dimensions, transparency requirement, color mode, file size, and ZIP size. Upload to LINE Creators Market, pricing, and sales submission remain manual.
