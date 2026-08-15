from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT_DIR = Path(__file__).resolve().parents[1]
THUMBNAIL_DIR = ROOT_DIR / "folio_app" / "static" / "powerbi_learning_thumbs"


@dataclass(frozen=True)
class StepResult:
    name: str
    status: str
    detail: str = ""


@dataclass(frozen=True)
class Collector:
    name: str
    skip_attr: str
    command_builder: Callable[[argparse.Namespace], list[str]]


CSV_OUTPUTS = {
    "desktop": ROOT_DIR / "docs" / "curation" / "powerbi_desktop_download" / "all.csv",
    "updates": ROOT_DIR / "docs" / "curation" / "powerbi_updates" / "all.csv",
    "changelog": ROOT_DIR / "docs" / "curation" / "powerbi_changelog" / "all.csv",
    "learning_videos": ROOT_DIR / "docs" / "curation" / "powerbi_learning_videos" / "all.csv",
    "update_videos": ROOT_DIR / "docs" / "curation" / "powerbi_update_videos" / "all.csv",
    "learning_programs": ROOT_DIR / "docs" / "curation" / "powerbi_learning_programs" / "all.csv",
    "community_blog": ROOT_DIR / "docs" / "curation" / "powerbi_community_blog" / "all.csv",
}

THUMBNAIL_CSVS = (
    CSV_OUTPUTS["learning_videos"],
    CSV_OUTPUTS["update_videos"],
    CSV_OUTPUTS["learning_programs"],
)

COLLECTORS = (
    Collector(
        "Desktop download",
        "skip_desktop",
        lambda args: ["tools/collect_powerbi_desktop_download.py"],
    ),
    Collector(
        "Monthly updates",
        "skip_updates",
        lambda args: _release_command(
            "tools/collect_powerbi_updates.py",
            args.since_year,
            args.max_update_releases,
        ),
    ),
    Collector(
        "Desktop changelog",
        "skip_changelog",
        lambda args: _release_command(
            "tools/collect_powerbi_changelog.py",
            args.since_year,
            args.max_changelog_releases,
        ),
    ),
    Collector(
        "Learning videos and programs",
        "skip_learning",
        lambda args: ["tools/collect_powerbi_learning_videos.py"],
    ),
    Collector(
        "Community blog",
        "skip_community",
        lambda args: ["tools/collect_powerbi_community_blog.py", "--limit", str(args.community_limit)],
    ),
)


def main() -> int:
    args = _parse_args()
    results: list[StepResult] = []

    for collector in COLLECTORS:
        if getattr(args, collector.skip_attr):
            continue
        results.append(_run_step(collector.name, collector.command_builder(args), dry_run=args.dry_run))
    if not args.skip_thumbnail_cleanup:
        results.append(_cleanup_thumbnails(dry_run=args.dry_run))
    if not args.skip_reference_check:
        results.append(_check_powerbi_reference())
    if not args.skip_validation:
        results.extend(_validate_outputs())

    _print_summary(results)
    return 1 if any(result.status == "failed" for result in results) else 0


def _release_command(script_path: str, since_year: int, max_releases: int) -> list[str]:
    command = [script_path, "--since-year", str(since_year)]
    if max_releases:
        command.extend(["--max-releases", str(max_releases)])
    return command


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect all Power BI content sources used by the FOLIO Power BI hub.",
    )
    parser.add_argument("--since-year", type=int, default=2025, help="Start year for Microsoft Learn updates and changelog.")
    parser.add_argument("--max-update-releases", type=int, default=0, help="Limit monthly update releases. 0 means no limit.")
    parser.add_argument("--max-changelog-releases", type=int, default=0, help="Limit changelog releases. 0 means no limit.")
    parser.add_argument("--community-limit", type=int, default=30, help="Maximum community blog posts to collect.")
    parser.add_argument("--skip-desktop", action="store_true", help="Skip Power BI Desktop download metadata.")
    parser.add_argument("--skip-updates", action="store_true", help="Skip monthly update archive.")
    parser.add_argument("--skip-changelog", action="store_true", help="Skip Desktop changelog.")
    parser.add_argument("--skip-learning", action="store_true", help="Skip YouTube learning/update videos and program playlists.")
    parser.add_argument("--skip-community", action="store_true", help="Skip Microsoft Fabric Community Blog RSS.")
    parser.add_argument("--skip-thumbnail-cleanup", action="store_true", help="Skip cleanup of unused local YouTube thumbnails.")
    parser.add_argument("--skip-reference-check", action="store_true", help="Skip Power BI official reference configuration check.")
    parser.add_argument("--skip-validation", action="store_true", help="Skip output CSV validation.")
    parser.add_argument("--dry-run", action="store_true", help="Print the collection plan without running network collectors.")
    return parser.parse_args()


def _run_step(name: str, command: list[str], *, dry_run: bool) -> StepResult:
    full_command = [sys.executable, *command]
    if dry_run:
        return StepResult(name, "skipped", " ".join(full_command))
    print(f"\n== {name} ==")
    try:
        completed = subprocess.run(
            full_command,
            cwd=ROOT_DIR,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            check=False,
            text=True,
            capture_output=True,
        )
    except OSError as exc:
        return StepResult(name, "failed", str(exc))
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip(), file=sys.stderr)
    if completed.returncode != 0:
        return StepResult(name, "failed", f"exit={completed.returncode}")
    return StepResult(name, "ok")


def _cleanup_thumbnails(*, dry_run: bool) -> StepResult:
    keep = _referenced_thumbnail_names()
    if not THUMBNAIL_DIR.exists():
        return StepResult("Thumbnail cleanup", "ok", "thumbnail directory does not exist")
    removable = [
        path
        for path in THUMBNAIL_DIR.iterdir()
        if path.is_file() and path.name not in keep
    ]
    if dry_run:
        return StepResult("Thumbnail cleanup", "skipped", f"{len(removable)} files would be removed")
    for path in removable:
        if THUMBNAIL_DIR.resolve() not in path.resolve().parents:
            return StepResult("Thumbnail cleanup", "failed", f"unsafe path: {path}")
        path.unlink()
    return StepResult("Thumbnail cleanup", "ok", f"removed={len(removable)}")


def _referenced_thumbnail_names() -> set[str]:
    names: set[str] = set()
    for path in THUMBNAIL_CSVS:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                asset = row.get("thumbnail_asset") or ""
                if asset:
                    names.add(Path(asset).name)
    return names


def _check_powerbi_reference() -> StepResult:
    sys.path.insert(0, str(ROOT_DIR))
    try:
        from folio_app.services.project_references import REFERENCE_PLATFORM_BY_KEY
    except Exception as exc:
        return StepResult("Official reference check", "failed", f"import failed: {exc}")
    platform = REFERENCE_PLATFORM_BY_KEY.get("powerbi")
    logo = ROOT_DIR / "folio_app" / "static" / "reference-powerbi-logo-cropped.webp"
    if not platform:
        return StepResult("Official reference check", "failed", "missing powerbi platform")
    if not logo.exists():
        return StepResult("Official reference check", "failed", f"missing logo: {logo.relative_to(ROOT_DIR)}")
    return StepResult("Official reference check", "ok", f"label={platform.label}")


def _validate_outputs() -> list[StepResult]:
    results = []
    for name, path in CSV_OUTPUTS.items():
        if not path.exists():
            results.append(StepResult(f"Validate {name}", "failed", f"missing {path.relative_to(ROOT_DIR)}"))
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            count = sum(1 for _ in csv.DictReader(handle))
        if count < 1:
            results.append(StepResult(f"Validate {name}", "failed", "no rows"))
        else:
            results.append(StepResult(f"Validate {name}", "ok", f"rows={count}"))
    return results


def _print_summary(results: list[StepResult]) -> None:
    print("\n== Power BI collection summary ==")
    for result in results:
        suffix = f" ({result.detail})" if result.detail else ""
        print(f"- {result.status.upper()}: {result.name}{suffix}")


if __name__ == "__main__":
    raise SystemExit(main())
