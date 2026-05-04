from __future__ import annotations

from .images import make_contact_sheet
from .project import Project


def build_contact_sheet(project: Project) -> None:
    images = sorted(project.final_dir.glob("*.png"))
    make_contact_sheet(images, project.reports_dir / "contact_sheet.png", f"{project.name} {project.kind}")
