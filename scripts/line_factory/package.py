from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from .images import has_transparency
from .project import Project
from .reports import build_all_reports
from .specs import expected_images, load_kind_spec
from .validate import validate_project


class PackageError(RuntimeError):
    pass


def package_name(project: Project) -> str:
    suffix = "line_stickers.zip" if project.kind == "static_sticker" else "line_emoji.zip"
    return f"{project.name}_{suffix}"


def package_project(project: Project) -> Path:
    result = build_all_reports(project)
    if not result.ok:
        raise PackageError("Validation has fatal errors; package blocked.")
    spec = load_kind_spec(project.kind)
    expected = expected_images(project.kind, project.count, spec)
    project.dist_dir.mkdir(parents=True, exist_ok=True)
    zip_path = project.dist_dir / package_name(project)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for exp in expected:
            src = project.final_dir / exp.filename
            zf.write(src, exp.filename)
    verify_zip(project, zip_path)
    return zip_path


def verify_zip(project: Project, zip_path: Path) -> None:
    spec = load_kind_spec(project.kind)
    expected = expected_images(project.kind, project.count, spec)
    expected_names = [e.filename for e in expected]
    expected_by_name = {e.filename: e for e in expected}
    max_zip_bytes = int(spec["limits"]["max_zip_bytes"])
    if zip_path.stat().st_size > max_zip_bytes:
        raise PackageError(f"ZIP exceeds size limit: {zip_path.stat().st_size} > {max_zip_bytes}")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            if names != expected_names:
                raise PackageError(f"ZIP contents mismatch: {names} != {expected_names}")
            for info in zf.infolist():
                if info.file_size > int(spec["limits"]["max_image_bytes"]):
                    raise PackageError(f"{info.filename}: file inside ZIP exceeds image limit")
                data = zf.read(info)
                if data[:8] != b"\x89PNG\r\n\x1a\n":
                    raise PackageError(f"{info.filename}: not a PNG in ZIP")
                exp = expected_by_name[info.filename]
                try:
                    with Image.open(BytesIO(data)) as img:
                        img.load()
                        if img.format != "PNG":
                            raise PackageError(f"{info.filename}: not a PNG in ZIP")
                        if img.mode not in ("RGBA", "RGB", "P", "LA"):
                            raise PackageError(f"{info.filename}: unsupported color mode {img.mode} in ZIP")
                        width, height = img.size
                        if exp.width is not None and width != exp.width:
                            raise PackageError(f"{info.filename}: ZIP width {width} != {exp.width}")
                        if exp.height is not None and height != exp.height:
                            raise PackageError(f"{info.filename}: ZIP height {height} != {exp.height}")
                        if exp.max_width is not None and width > exp.max_width:
                            raise PackageError(f"{info.filename}: ZIP width {width} exceeds {exp.max_width}")
                        if exp.max_height is not None and height > exp.max_height:
                            raise PackageError(f"{info.filename}: ZIP height {height} exceeds {exp.max_height}")
                        if exp.even_dimensions and (width % 2 or height % 2):
                            raise PackageError(f"{info.filename}: ZIP dimensions must be even numbers")
                        if exp.required_alpha and not has_transparency(img):
                            raise PackageError(f"{info.filename}: ZIP item image must have transparency")
                except PackageError:
                    raise
                except Exception as exc:
                    raise PackageError(f"{info.filename}: cannot re-open PNG in ZIP ({exc})") from exc
    except zipfile.BadZipFile as exc:
        raise PackageError(f"Invalid ZIP archive: {exc}") from exc


def zip_listing(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        return zf.namelist()
