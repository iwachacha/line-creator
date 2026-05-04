# 05 Finish

Input: PNGs in `assets/source/`.

Command:

```powershell
python -m line_factory.cli finish --project projects/<name>
```

Output: LINE-ready PNGs in `assets/final/` and `reports/contact_sheet.png`.

Behavior: normalize transparent PNGs to required canvas size and naming. For static stickers, create `main.png`, `tab.png`, and `01.png` etc. For regular emoji, create `tab.png` and `001.png` etc.
