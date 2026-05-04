from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from .contact_sheet import build_contact_sheet
from .images import open_png
from .project import Project


def build_visual_report(project: Project) -> str:
    build_contact_sheet(project)
    visual_png = build_visual_report_image(project)
    final_gate = (
        "- Automated approval policy is active; use this report as package-readiness evidence."
        if project.uses_automated_approvals
        else "- ZIP upload must wait for HAG-5 approval."
    )
    generation_gate = (
        "- If generated artwork was used, review `reports/generation_qa_checklist.md` before packaging."
        if project.uses_automated_approvals
        else "- If generated artwork was used, review `reports/generation_qa_checklist.md` before HAG-5."
    )
    text = "\n".join(
        [
            f"# Visual Report: {project.name}",
            "",
            "Review `contact_sheet.png` and `visual_report.png` for readability, expression balance, typos, background removal, and review-risk concerns.",
            "",
            "- Contact sheet: `reports/contact_sheet.png`",
            "- Visual QA sheet: `reports/visual_report.png`",
            generation_gate,
            "- Confirm integrated text belongs to the artwork and is not a detached generic label unless explicitly style-locked.",
            "- Confirm the artwork reads as LINE sticker/emoji art, not a physical sticker mockup.",
            final_gate,
            "",
        ]
    )
    project.reports_dir.mkdir(parents=True, exist_ok=True)
    (project.reports_dir / "visual_report.md").write_text(text, encoding="utf-8")
    return text


def build_visual_report_image(project: Project) -> str:
    image_paths = sorted(project.final_dir.glob("*.png"))
    thumbs = []
    for path in image_paths:
        img = open_png(path).convert("RGBA")
        img.thumbnail((112, 112), Image.Resampling.LANCZOS)
        chat = open_png(path).convert("RGBA")
        chat.thumbnail((56, 56), Image.Resampling.LANCZOS)
        thumbs.append((path.name, img.copy(), chat.copy()))
        img.close()
        chat.close()

    font = ImageFont.load_default()
    cols = 3
    rows = max(1, len(thumbs))
    label_w = 92
    cell_w = 136
    chat_w = 96
    row_h = 142
    header_h = 34
    sheet = Image.new("RGB", (label_w + cols * cell_w + chat_w, header_h + rows * row_h), "white")
    draw = ImageDraw.Draw(sheet)
    headers = [("checker", label_w), ("white", label_w + cell_w), ("dark", label_w + cell_w * 2), ("chat", label_w + cell_w * 3)]
    draw.text((10, 12), "file", fill=(20, 20, 20), font=font)
    for text, x in headers:
        draw.text((x + 10, 12), text, fill=(20, 20, 20), font=font)

    for row, (name, img, chat) in enumerate(thumbs):
        y = header_h + row * row_h
        draw.text((10, y + 58), name, fill=(20, 20, 20), font=font)
        paste_preview(sheet, img, label_w, y, cell_w, row_h, "checker")
        paste_preview(sheet, img, label_w + cell_w, y, cell_w, row_h, "white")
        paste_preview(sheet, img, label_w + cell_w * 2, y, cell_w, row_h, "dark")
        paste_preview(sheet, chat, label_w + cell_w * 3, y, chat_w, row_h, "white")
    output = project.reports_dir / "visual_report.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "PNG")
    return str(output)


def paste_preview(sheet: Image.Image, img: Image.Image, x: int, y: int, w: int, h: int, mode: str) -> None:
    if mode == "checker":
        bg = checkerboard((w, h))
    elif mode == "dark":
        bg = Image.new("RGBA", (w, h), (28, 28, 28, 255))
    else:
        bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    px = x + (w - img.width) // 2
    py = y + (h - img.height) // 2
    bg.alpha_composite(img, (px - x, py - y))
    draw = ImageDraw.Draw(bg)
    draw.rectangle((0, 0, w - 1, h - 1), outline=(215, 215, 215))
    sheet.paste(bg.convert("RGB"), (x, y))


def checkerboard(size: tuple[int, int], step: int = 12) -> Image.Image:
    bg = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                draw.rectangle((x, y, x + step - 1, y + step - 1), fill=(220, 220, 220, 255))
    return bg
