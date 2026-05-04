from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


PNG_SUFFIX = ".png"


def list_source_pngs(source_dir: Path) -> list[Path]:
    return sorted(p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() == PNG_SUFFIX)


def open_png(path: Path) -> Image.Image:
    img = Image.open(path)
    img.load()
    return img


def alpha_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    rgba = img.convert("RGBA")
    return rgba.getchannel("A").getbbox()


def alpha_coverage(img: Image.Image) -> float:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    total = alpha.width * alpha.height
    if total == 0:
        return 0.0
    nonzero = sum(1 for v in alpha.getdata() if v > 0)
    return nonzero / total


def edge_alpha_coverage(img: Image.Image, edge_px: int = 2) -> float:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = alpha.size
    if width == 0 or height == 0:
        return 0.0
    pixels = alpha.load()
    total = 0
    nonzero = 0
    for y in range(height):
        for x in range(width):
            if x < edge_px or y < edge_px or x >= width - edge_px or y >= height - edge_px:
                total += 1
                if pixels[x, y] > 0:
                    nonzero += 1
    return nonzero / total if total else 0.0


def opaque_bbox_fill_ratio(img: Image.Image) -> float:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return 0.0
    cropped = alpha.crop(bbox)
    total = cropped.width * cropped.height
    if total == 0:
        return 0.0
    opaque = sum(1 for v in cropped.getdata() if v >= 250)
    return opaque / total


def corner_alpha_values(img: Image.Image) -> list[int]:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = alpha.size
    if width == 0 or height == 0:
        return []
    return [
        alpha.getpixel((0, 0)),
        alpha.getpixel((width - 1, 0)),
        alpha.getpixel((0, height - 1)),
        alpha.getpixel((width - 1, height - 1)),
    ]


def chroma_key_edge_ratio(img: Image.Image, colors: list[tuple[int, int, int]], tolerance: int = 30, edge_px: int = 3) -> float:
    rgba = img.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    total = 0
    matches = 0
    for y in range(height):
        for x in range(width):
            if not (x < edge_px or y < edge_px or x >= width - edge_px or y >= height - edge_px):
                continue
            total += 1
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            for kr, kg, kb in colors:
                if abs(r - kr) <= tolerance and abs(g - kg) <= tolerance and abs(b - kb) <= tolerance:
                    matches += 1
                    break
    return matches / total if total else 0.0


def visible_luma_delta(img: Image.Image, background: tuple[int, int, int]) -> float:
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return 0.0
    rgb = rgba.crop(bbox).convert("RGB")
    alpha_crop = alpha.crop(bbox)
    values = []
    bg_luma = 0.2126 * background[0] + 0.7152 * background[1] + 0.0722 * background[2]
    for (r, g, b), a in zip(rgb.getdata(), alpha_crop.getdata()):
        if a > 24:
            luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
            values.append(abs(luma - bg_luma))
    return sum(values) / len(values) if values else 0.0


def has_transparency(img: Image.Image) -> bool:
    if img.mode in ("RGBA", "LA"):
        return img.getchannel("A").getextrema()[0] < 255
    if img.mode == "P" and "transparency" in img.info:
        return True
    return False


def fit_to_canvas(img: Image.Image, width: int, height: int, margin: int = 0) -> Image.Image:
    rgba = img.convert("RGBA")
    bbox = alpha_bbox(rgba) or rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    max_w = max(1, width - margin * 2)
    max_h = max(1, height - margin * 2)
    rgba.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = (width - rgba.width) // 2
    y = (height - rgba.height) // 2
    canvas.alpha_composite(rgba, (x, y))
    return canvas


def fit_within_max(img: Image.Image, max_width: int, max_height: int, margin: int = 10) -> Image.Image:
    width = max_width
    height = max_height
    if width % 2:
        width -= 1
    if height % 2:
        height -= 1
    return fit_to_canvas(img, width, height, margin)


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def make_contact_sheet(image_paths: list[Path], output: Path, title: str = "Contact Sheet") -> None:
    thumbs: list[tuple[Path, Image.Image]] = []
    for p in image_paths:
        img = open_png(p).convert("RGBA")
        img.thumbnail((120, 120), Image.Resampling.LANCZOS)
        thumbs.append((p, img.copy()))
    cols = 5
    cell_w, cell_h = 160, 155
    header_h = 36
    rows = max(1, (len(thumbs) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * cell_w, header_h + rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 10), title, fill=(20, 20, 20), font=ImageFont.load_default())
    for i, (path, img) in enumerate(thumbs):
        col = i % cols
        row = i // cols
        x0 = col * cell_w
        y0 = header_h + row * cell_h
        draw.rectangle((x0 + 6, y0 + 6, x0 + cell_w - 6, y0 + cell_h - 6), outline=(220, 220, 220))
        bg = Image.new("RGBA", img.size, (245, 245, 245, 255))
        bg.alpha_composite(img)
        sheet.paste(bg.convert("RGB"), (x0 + (cell_w - img.width) // 2, y0 + 16))
        draw.text((x0 + 10, y0 + 128), path.name, fill=(40, 40, 40), font=ImageFont.load_default())
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "PNG")


def average_hash(img: Image.Image, size: int = 8) -> int:
    gray = img.convert("L").resize((size, size), Image.Resampling.BILINEAR)
    pixels = list(gray.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for p in pixels:
        bits = (bits << 1) | int(p >= avg)
    return bits


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()
