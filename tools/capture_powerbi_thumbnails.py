from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import create_client

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from folio_app.services.project_normalizers import THUMBNAIL_MODE_CAPTURE
from folio_app.services.project_references import reference_platform_for_project
from folio_app.services.project_thumbnails import (
    capture_thumbnail_bytes,
    thumbnail_capture_source_url,
    upload_project_thumbnail,
)


def main() -> int:
    load_dotenv(ROOT_DIR / ".env")
    args = _parse_args()
    client = create_client(_required_env("SUPABASE_URL"), _required_env("SUPABASE_SERVICE_ROLE_KEY"))
    projects = _powerbi_projects(_fetch_projects(client))
    if args.only_missing_thumbnail:
        projects = [project for project in projects if not (project.get("thumbnail_url") or "").strip()]
    if args.limit:
        projects = projects[: args.limit]

    print(f"powerbi_projects={len(projects)}")
    if args.dry_run:
        for project in projects:
            print(f"DRY {project['id']} {project.get('title')}")
        return 0

    ok = 0
    failed = 0
    skipped = 0
    for index, project in enumerate(projects, start=1):
        project_id = project["id"]
        title = project.get("title") or project_id
        print(f"[{index}/{len(projects)}] start {project_id} {title}", flush=True)
        try:
            client.table("projects").update({"thumbnail_mode": THUMBNAIL_MODE_CAPTURE}).eq("id", project_id).execute()
            source_url = thumbnail_capture_source_url(project)
            if not source_url:
                skipped += 1
                print(f"[{index}/{len(projects)}] skipped_no_source {project_id}", flush=True)
                continue
            image_bytes = capture_thumbnail_bytes(source_url, progress_callback=_progress_logger(index, len(projects)))
            thumbnail_url = upload_project_thumbnail(project_id, image_bytes, client=client)
            client.table("projects").update(
                {
                    "thumbnail_mode": THUMBNAIL_MODE_CAPTURE,
                    "thumbnail_url": thumbnail_url,
                }
            ).eq("id", project_id).execute()
            ok += 1
            print(f"[{index}/{len(projects)}] ok {project_id} {thumbnail_url}", flush=True)
        except Exception as exc:
            failed += 1
            print(f"[{index}/{len(projects)}] failed {project_id} {type(exc).__name__}: {exc}", flush=True)

    print(f"done ok={ok} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set Power BI projects to capture mode and capture thumbnails.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only-missing-thumbnail", action="store_true")
    return parser.parse_args()


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _fetch_projects(client: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page_size = 1000
    start = 0
    while True:
        response = (
            client.table("projects")
            .select("id,title,tags,power_bi_url,report_url,github_url,thumbnail_url,thumbnail_mode")
            .range(start, start + page_size - 1)
            .execute()
        )
        batch = response.data or []
        rows.extend(batch)
        if len(batch) < page_size:
            return rows
        start += page_size


def _powerbi_projects(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [project for project in projects if reference_platform_for_project(project) == "powerbi"]


def _progress_logger(index: int, total: int):
    def log(value: int, text: str) -> None:
        print(f"[{index}/{total}] capture {value}% {text}", flush=True)

    return log


if __name__ == "__main__":
    raise SystemExit(main())
