from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import create_client

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from folio_app.services.project_normalizers import clean_project_payload


DEFAULT_CSV_PATH = Path("docs/curation/streamlit_gallery/all.csv")
DEFAULT_ADMIN_EMAIL = "admin@folio.com"


def main() -> int:
    load_dotenv()
    args = _parse_args()

    rows = _read_rows(args.csv_path)
    if args.limit:
        rows = rows[: args.limit]

    if not rows:
        print("No rows to import.")
        return 0

    client = create_client(_required_env("SUPABASE_URL"), _required_env("SUPABASE_PUBLISHABLE_KEY"))
    auth_response = client.auth.sign_in_with_password(
        {
            "email": args.admin_email,
            "password": _required_env("FOLIO_ADMIN_PASSWORD"),
        }
    )
    if auth_response.user is None or auth_response.session is None:
        raise RuntimeError("Admin sign-in failed.")

    admin_id = auth_response.user.id
    client.postgrest.auth(auth_response.session.access_token)

    existing_urls = _existing_project_urls(client)
    payloads = []
    skipped = 0
    for row in rows:
        source_url = row.get("source_url", "").strip()
        if source_url in existing_urls:
            skipped += 1
            continue
        payload = _project_payload_from_row(row)
        payload["author_id"] = admin_id
        payloads.append(payload)

    print(f"CSV rows: {len(rows)}")
    print(f"Already exists: {skipped}")
    print(f"Will insert: {len(payloads)}")

    if args.dry_run or not args.execute:
        print("Dry run only. Add --execute to insert projects.")
        for preview in payloads[:5]:
            print(f"- {preview['title']} ({preview.get('report_url') or preview.get('power_bi_url')})")
        return 0

    inserted = 0
    for payload in payloads:
        client.table("projects").insert(payload).execute()
        inserted += 1
        print(f"Inserted {inserted}/{len(payloads)}: {payload['title']}")

    print(f"Done. Inserted {inserted} projects as {args.admin_email}.")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import Streamlit Gallery CSV rows into FOLIO projects as an admin user.",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help=f"CSV path. Defaults to {DEFAULT_CSV_PATH}.",
    )
    parser.add_argument(
        "--admin-email",
        default=DEFAULT_ADMIN_EMAIL,
        help=f"Admin account email. Defaults to {DEFAULT_ADMIN_EMAIL}.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Import at most N rows.")
    parser.add_argument("--execute", action="store_true", help="Actually insert rows.")
    parser.add_argument("--dry-run", action="store_true", help="Preview only. This is the default.")
    return parser.parse_args()


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _existing_project_urls(client: Any) -> set[str]:
    response = client.table("projects").select("report_url,power_bi_url").execute()
    urls = set()
    for row in response.data or []:
        for key in ("report_url", "power_bi_url"):
            value = (row.get(key) or "").strip()
            if value:
                urls.add(value)
    return urls


def _project_payload_from_row(row: dict[str, str]) -> dict[str, Any]:
    categories = _split_categories(row.get("categories", ""))
    primary_category = next((category for category in categories if category != "Favorites"), "")
    tags = ["Streamlit", *categories]
    summary = f"Streamlit Gallery {primary_category or '추천'} 카테고리에 소개된 공개 앱입니다."
    source_url = row.get("source_url", "").strip()
    github_url = row.get("github_url", "").strip()

    payload = clean_project_payload(
        {
            "title": row.get("title", ""),
            "one_liner": summary,
            "problem": _paragraph(
                "이 프로젝트는 Streamlit 공식 갤러리에 공개된 앱으로, "
                "FOLIO에서 큐레이션 후보 콘텐츠로 수집했습니다."
            ),
            "dataset": _paragraph("원본 앱과 저장소를 검토한 뒤 사용 데이터 설명을 보강해야 합니다."),
            "process": _paragraph("앱의 주요 화면과 상호작용을 확인한 뒤 분석 및 시각화 방식을 정리해야 합니다."),
            "insights": _paragraph("사용자가 앱을 볼 때 주목할 관찰 포인트를 운영자 검토 후 작성해야 합니다."),
            "power_bi_url": row.get("embed_url", ""),
            "report_url": source_url,
            "github_url": github_url,
            "thumbnail_url": row.get("thumbnail_url", ""),
            "tags": tags,
            "is_public": True,
        }
    )
    return payload


def _split_categories(value: str) -> list[str]:
    categories = []
    for category in value.split(";"):
        normalized = category.strip()
        if normalized and normalized not in categories:
            categories.append(normalized)
    return categories


def _paragraph(value: str) -> str:
    return f"<p>{value}</p>"


if __name__ == "__main__":
    raise SystemExit(main())
