from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .finish import finish_project
from .generation import write_generation_qa_checklist, write_image_generation_plan
from .package import PackageError, package_project, zip_listing
from .project import init_project, load_project
from .reports import build_all_reports, write_validation_report
from .validate import validate_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m line_factory.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a project from projects/_template")
    init.add_argument("--project", required=True)
    init.add_argument("--kind", choices=["static_sticker", "regular_emoji"], default="static_sticker")
    init.add_argument("--count", type=int, default=8)
    init.add_argument("--force", action="store_true")
    init.add_argument(
        "--approval-policy",
        choices=["manual", "automated"],
        default="manual",
        help="Use manual HAG enforcement or explicit automated approval-gate waiver.",
    )

    for name in ["generate-plan", "finish", "validate", "package", "report"]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--project", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            project = init_project(args.project, args.kind, args.count, args.force, args.approval_policy)
            print(f"Initialized {project.kind} project at {project.path}")
            if project.uses_automated_approvals:
                print("Approval policy: automated. HAG gates are waived for CLI packaging.")
            else:
                print("Human approval required: HAG-1 and HAG-2 before style or production work.")
            return 0
        project = load_project(args.project)
        if args.command == "generate-plan":
            plan_path = write_image_generation_plan(project)
            qa_path = write_generation_qa_checklist(project)
            print(f"Generated image generation plan: {plan_path}")
            print(f"Generated generation QA checklist: {qa_path}")
            print("Use Codex built-in image_gen via the imagegen skill, then copy accepted PNGs into assets/source/.")
            print("Do not use placeholder or fallback art for production unless the user explicitly approves it.")
            return 0
        if args.command == "finish":
            outputs = finish_project(project)
            print(f"Finished {len(outputs)} PNG files into {project.final_dir}")
            print(f"Generated contact sheet: {project.reports_dir / 'contact_sheet.png'}")
            if project.uses_automated_approvals:
                print("Approval policy: automated. Continue with validate/package after automated QA.")
            else:
                print("Human approval required: HAG-5 before manual upload.")
            return 0
        if args.command == "validate":
            result = validate_project(project)
            write_validation_report(project, result)
            print(f"Validation {'PASS' if result.ok else 'FAIL'}")
            print(f"Report: {project.reports_dir / 'validation.md'}")
            if not result.ok:
                return 2
            return 0
        if args.command == "package":
            zip_path = package_project(project)
            print(f"Created ZIP: {zip_path}")
            print("ZIP contents:")
            for name in zip_listing(zip_path):
                print(f"  {name}")
            print("Manual action remains: LINE Creators Market upload, pricing, and sales submission.")
            return 0
        if args.command == "report":
            result = build_all_reports(project)
            print(f"Reports generated in {project.reports_dir}")
            return 0 if result.ok else 2
    except (FileNotFoundError, ValueError, RuntimeError, PackageError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    parser.error("Unhandled command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
