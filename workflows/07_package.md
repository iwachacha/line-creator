# 07 Package

Input: validated final PNGs, generated reports, and HAG-5 approval.

Command:

```powershell
python -m line_factory.cli package --project projects/<name>
```

Output: `dist/<project>_line_stickers.zip` or `dist/<project>_line_emoji.zip`.

The CLI refuses packaging when validation has fatal errors or any HAG-1 through HAG-5 approval is pending in `project.yml`.

After writing the ZIP, the CLI re-opens every PNG inside the archive and verifies expected order, filename, dimensions, transparency requirement, color mode, file size, and ZIP size. Upload to LINE Creators Market, pricing, and sales submission remain manual.
