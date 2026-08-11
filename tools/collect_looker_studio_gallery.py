from __future__ import annotations

import argparse
import csv
import html
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from folio_app.services.project_normalizers import clean_project_payload


DEFAULT_GALLERY_URL = "https://datastudio.google.com/gallery"
DEFAULT_OUTPUT_PATH = Path("docs/curation/looker_studio_gallery/all.csv")
DEFAULT_ADMIN_EMAIL = "admin@folio.com"
CATEGORY_URL_SLUGS = {
    "Featured": "featured",
    "Marketing Templates": "marketing",
    "Community": "community",
    "Community Visualizations": "visualization",
}
INACCESSIBLE_TEXT_MARKERS = (
    "보고서에 액세스할 수 없음",
    "보고서 소유자가 다른 웹사이트에서 보기를 사용 중지했습니다",
    "you can't access",
    "you cannot access",
    "this report is not available",
    "the report owner has disabled viewing on other websites",
)
SYSTEM_ERROR_TEXT_MARKERS = (
    "데이터 스튜디오에서 시스템 오류가 발생했습니다",
    "looker studio has encountered a system error",
    "data studio has encountered a system error",
)

FIELDNAMES = [
    "index",
    "title",
    "platform",
    "creator_name",
    "creator_url",
    "source_url",
    "embed_url",
    "thumbnail_url",
    "github_url",
    "categories",
    "source_type",
    "embed_status",
    "publication_status",
    "weight",
    "collected_from",
    "collected_category",
    "collected_at",
    "description",
    "open_url",
    "status",
    "registered_project_id",
]


def main() -> int:
    args = _parse_args()
    rows = collect_looker_studio_gallery(args)
    print(f"Collected rows: {len(rows)}")
    print(f"Collected embeds: {sum(row.get('status') == 'collected' for row in rows)}")
    print(f"Saved: {args.output}")
    if args.register:
        summary = register_collected_rows(args, rows)
        print(f"Registered: {summary['inserted']}")
        print(f"Already existed: {summary['existing']}")
        print(f"Registration skipped: {summary['skipped']}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Looker Studio gallery reports into a FOLIO curation CSV.",
    )
    parser.add_argument("--url", default=DEFAULT_GALLERY_URL, help=f"Gallery URL. Defaults to {DEFAULT_GALLERY_URL}.")
    parser.add_argument(
        "--category",
        action="append",
        choices=sorted(CATEGORY_URL_SLUGS),
        default=[],
        help="Gallery category label to collect. May be repeated.",
    )
    parser.add_argument("--all-categories", action="store_true", help="Collect every known gallery category.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"CSV output path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    parser.add_argument("--wait-seconds", type=float, default=8.0, help="Seconds to wait on gallery/report pages.")
    parser.add_argument("--embed-wait-seconds", type=float, default=5.0, help="Seconds to wait on embed pages.")
    parser.add_argument("--start-index", type=int, default=1, help="First 1-based gallery item index to collect.")
    parser.add_argument("--end-index", type=int, default=0, help="Last 1-based gallery item index to collect.")
    parser.add_argument("--only-index", type=int, action="append", default=[], help="Only collect this index.")
    parser.add_argument("--skip-index", type=int, action="append", default=[], help="Skip this index.")
    parser.add_argument("--force", action="store_true", help="Re-collect rows already present in the output CSV.")
    parser.add_argument("--headless", action="store_true", help="Run Chrome headless.")
    parser.add_argument("--register", action="store_true", help="Insert collected rows into Supabase projects.")
    parser.add_argument("--admin-email", default=DEFAULT_ADMIN_EMAIL, help="Admin account email for --register.")
    return parser.parse_args()


def collect_looker_studio_gallery(args: argparse.Namespace) -> list[dict[str, str]]:
    existing_rows = _read_rows(args.output)
    output_rows: list[dict[str, str]] = [dict(row) for row in existing_rows]
    rows_by_identity = {_row_identity(row): row for row in output_rows if _row_identity(row)}
    rows_by_open_url = {row.get("open_url", ""): row for row in output_rows if row.get("open_url")}

    driver = webdriver.Chrome(options=_chrome_options(args.headless))
    try:
        for category_label, category_url in _category_urls(args):
            gallery_items = _collect_gallery_items(driver, category_url, args.wait_seconds, category_label)
            print(f"{category_label} gallery items: {len(gallery_items)}")
            for index, item in enumerate(gallery_items, start=1):
                if not _should_collect_index(args, index):
                    continue

                identity = _item_identity(item)
                existing = rows_by_identity.get(identity) or rows_by_open_url.get(item["open_url"])
                if existing and not args.force:
                    print(f"[{index}/{len(gallery_items)}] reuse {existing.get('status', 'collected')} {existing.get('title')}")
                    if category_label and category_label not in (existing.get("categories") or ""):
                        existing["categories"] = _append_csv_value(existing.get("categories", ""), category_label)
                        existing["collected_category"] = _append_csv_value(existing.get("collected_category", ""), category_label)
                        _write_rows(args.output, output_rows)
                    continue

                print(f"[{index}/{len(gallery_items)}] collect {category_label} / {item['title']}", flush=True)
                row = _collect_one(driver, index, item, category_url, args.wait_seconds, args.embed_wait_seconds)
                print(f"    {row.get('status')} {row.get('title')}", flush=True)
                output_rows.append(row)
                rows_by_identity[_row_identity(row)] = row
                rows_by_open_url[row.get("open_url", "")] = row
                _write_rows(args.output, output_rows)
    finally:
        driver.quit()

    return output_rows


def _chrome_options(headless: bool) -> Options:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    return options


def _category_urls(args: argparse.Namespace) -> list[tuple[str, str]]:
    if args.all_categories:
        labels = list(CATEGORY_URL_SLUGS)
    elif args.category:
        labels = args.category
    else:
        labels = ["Featured"]
    return [(label, _gallery_url_for_category(args.url, label)) for label in labels]


def _gallery_url_for_category(base_url: str, category_label: str) -> str:
    slug = CATEGORY_URL_SLUGS[category_label]
    if slug == "featured":
        return DEFAULT_GALLERY_URL
    return f"{base_url.split('?')[0]}?category={slug}"


def _collect_gallery_items(driver: Any, gallery_url: str, wait_seconds: float, category_label: str) -> list[dict[str, str]]:
    driver.set_page_load_timeout(60)
    driver.get(gallery_url)
    time.sleep(wait_seconds)

    items: list[dict[str, str]] = []
    seen: set[str] = set()
    for anchor in driver.find_elements(By.CSS_SELECTOR, 'a.reportImageUrl[href*="datastudio.google.com/open/"]'):
        open_url = anchor.get_attribute("href") or ""
        if not open_url or open_url in seen:
            continue
        seen.add(open_url)
        items.append(
            {
                "title": _child_text(anchor, ".reportTitle"),
                "creator_name": _creator_name(anchor),
                "creator_url": _creator_url(anchor),
                "description": _child_text(anchor, ".reportDescription"),
                "open_url": open_url,
                "thumbnail_url": _thumbnail_url(anchor),
                "category_label": category_label,
            }
        )
    return items


def _child_text(element: Any, selector: str) -> str:
    try:
        return (element.find_element(By.CSS_SELECTOR, selector).text or "").strip()
    except Exception:
        return ""


def _creator_name(anchor: Any) -> str:
    try:
        return (anchor.find_element(By.CSS_SELECTOR, ".reportCreatedBy a").text or "").replace("By ", "").strip()
    except Exception:
        return ""


def _creator_url(anchor: Any) -> str:
    try:
        return anchor.find_element(By.CSS_SELECTOR, ".reportCreatedBy a").get_attribute("href") or ""
    except Exception:
        return ""


def _thumbnail_url(anchor: Any) -> str:
    try:
        return anchor.find_element(By.TAG_NAME, "img").get_attribute("src") or ""
    except Exception:
        return ""


def _should_collect_index(args: argparse.Namespace, index: int) -> bool:
    if args.only_index and index not in set(args.only_index):
        return False
    if index < args.start_index:
        return False
    if args.end_index and index > args.end_index:
        return False
    return index not in set(args.skip_index)


def _collect_one(
    driver: Any,
    index: int,
    item: dict[str, str],
    gallery_url: str,
    wait_seconds: float,
    embed_wait_seconds: float,
) -> dict[str, str]:
    row = _base_row(index, item, gallery_url)
    try:
        report_url, embed_url, resolved_title, embed_status = _resolve_report_and_embed_urls(
            driver,
            item["open_url"],
            wait_seconds,
            embed_wait_seconds,
        )
        if resolved_title and not row["title"]:
            row["title"] = resolved_title
        row["source_url"] = report_url
        row["embed_url"] = embed_url
        row["status"] = embed_status if embed_status != "ok" else "collected"
        return row
    except Exception as exc:
        row["status"] = f"error_{type(exc).__name__}"
        return row


def _base_row(index: int, item: dict[str, str], gallery_url: str) -> dict[str, str]:
    category_label = item.get("category_label") or "Featured"
    return {
        "index": str(index),
        "title": item.get("title", ""),
        "platform": "Looker Studio",
        "creator_name": item.get("creator_name", ""),
        "creator_url": item.get("creator_url", ""),
        "source_url": "",
        "embed_url": "",
        "thumbnail_url": item.get("thumbnail_url", ""),
        "github_url": "",
        "categories": category_label,
        "source_type": "curated",
        "embed_status": "unverified",
        "publication_status": "review",
        "weight": str(max(0, 1000000 - index * 10000)),
        "collected_from": gallery_url,
        "collected_category": category_label,
        "collected_at": datetime.now().replace(microsecond=0).isoformat(),
        "description": item.get("description", ""),
        "open_url": item.get("open_url", ""),
        "status": "",
        "registered_project_id": "",
    }


def _resolve_report_and_embed_urls(
    driver: Any,
    open_url: str,
    wait_seconds: float,
    embed_wait_seconds: float,
) -> tuple[str, str, str, str]:
    driver.set_page_load_timeout(60)
    driver.get(open_url)
    time.sleep(wait_seconds)
    report_url = driver.current_url
    resolved_title = _title_from_driver(driver)
    if "/reporting/" not in report_url:
        return "", "", resolved_title, "skipped_missing_report"

    embed_url = report_url.replace("https://datastudio.google.com/reporting/", "https://datastudio.google.com/embed/reporting/")
    driver.get(embed_url)
    time.sleep(embed_wait_seconds)
    body_text = (driver.find_element(By.TAG_NAME, "body").text or "").strip()
    if not body_text:
        return report_url, "", resolved_title, "skipped_blank_embed"
    status = _embed_body_status(body_text)
    if status != "ok":
        return report_url, "", resolved_title, status
    return report_url, embed_url, resolved_title, "ok"


def _embed_body_status(body_text: str) -> str:
    normalized = " ".join(body_text.lower().split())
    if any(marker.lower() in normalized for marker in INACCESSIBLE_TEXT_MARKERS):
        return "skipped_embed_access_disabled"
    if any(marker.lower() in normalized for marker in SYSTEM_ERROR_TEXT_MARKERS):
        return "skipped_embed_system_error"
    return "ok"


def _title_from_driver(driver: Any) -> str:
    title = (driver.title or "").strip()
    return re.sub(r"\s*›.*$", "", title).strip()


def register_collected_rows(args: argparse.Namespace, rows: list[dict[str, str]]) -> dict[str, int]:
    from supabase import create_client

    load_dotenv(ROOT_DIR / ".env")
    client = create_client(_required_env("SUPABASE_URL"), _required_env("SUPABASE_PUBLISHABLE_KEY"))
    auth_response = client.auth.sign_in_with_password(
        {
            "email": args.admin_email,
            "password": _required_env("FOLIO_ADMIN_PASSWORD"),
        }
    )
    if auth_response.user is None or auth_response.session is None:
        raise RuntimeError("Admin sign-in failed.")
    client.postgrest.auth(auth_response.session.access_token)

    existing_urls = _existing_project_urls(client)
    summary = {"inserted": 0, "existing": 0, "skipped": 0}
    for row in rows:
        if not _is_collected_row(row):
            summary["skipped"] += 1
            continue
        if row.get("source_url") in existing_urls or row.get("embed_url") in existing_urls:
            summary["existing"] += 1
            continue
        payload = _project_payload_from_row(row, auth_response.user.id)
        inserted = client.table("projects").insert(payload).execute()
        project = inserted.data[0] if inserted.data else {}
        row["registered_project_id"] = project.get("id") or ""
        existing_urls.add(row.get("source_url", ""))
        existing_urls.add(row.get("embed_url", ""))
        summary["inserted"] += 1
        print(f"Inserted {summary['inserted']}: {project.get('title')} {project.get('id')}")
    _write_rows(args.output, rows)
    return summary


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _existing_project_urls(client: Any) -> set[str]:
    response = client.table("projects").select("report_url,power_bi_url").execute()
    urls: set[str] = set()
    for row in response.data or []:
        for key in ("report_url", "power_bi_url"):
            value = (row.get(key) or "").strip()
            if value:
                urls.add(value)
    return urls


def _project_payload_from_row(row: dict[str, str], author_id: str) -> dict[str, Any]:
    title = row.get("title") or "Untitled Looker Studio Report"
    creator = row.get("creator_name") or "Looker Studio creator"
    payload = clean_project_payload(
        {
            "title": title,
            "one_liner": f"Looker Studio Gallery report: {title} by {creator}.",
            "problem": _paragraph(f"Gallery title: {title}. Creator: {creator}.") + _paragraph(row.get("description", "")),
            "dataset": _paragraph("This public Looker Studio gallery report uses the data sources configured by its original creator."),
            "process": _paragraph(
                "The gallery open URL was resolved to the public reporting URL, then converted to the verified Looker Studio embed URL. "
                "The thumbnail was collected from the gallery card image."
            ),
            "insights": _paragraph(
                "Use this Looker Studio gallery metadata as the initial FOLIO introduction. "
                "Editorial summary and source notes can be expanded after manual review."
            ),
            "power_bi_url": row.get("embed_url", ""),
            "report_url": row.get("source_url", ""),
            "github_url": "",
            "thumbnail_url": row.get("thumbnail_url", ""),
            "tags": _tags_from_row(row, creator),
            "is_public": True,
        }
    )
    payload["author_id"] = author_id
    return payload


def _paragraph(value: str) -> str:
    return f"<p>{html.escape(value)}</p>"


def _tags_from_row(row: dict[str, str], creator: str) -> list[str]:
    tags = ["Looker Studio", "Data Studio Gallery"]
    tags.extend(value.strip() for value in (row.get("categories") or "").split(",") if value.strip())
    if creator:
        tags.append(creator)
    return list(dict.fromkeys(tags))


def _is_collected_row(row: dict[str, str]) -> bool:
    return row.get("status", "") in ("", "collected") and bool(row.get("source_url") and row.get("embed_url"))


def _item_identity(item: dict[str, str]) -> str:
    return _identity_from_urls(item.get("open_url", ""), "")


def _row_identity(row: dict[str, str]) -> str:
    return _identity_from_urls(row.get("open_url", "") or row.get("source_url", ""), row.get("embed_url", ""))


def _identity_from_urls(primary_url: str, secondary_url: str) -> str:
    for value in (primary_url, secondary_url):
        match = re.search(r"/(?:open|reporting)/([^/?#]+)", value or "")
        if match:
            return match.group(1)
    return ""


def _append_csv_value(existing: str, value: str) -> str:
    values = [item.strip() for item in existing.split(",") if item.strip()]
    if value not in values:
        values.append(value)
    return ", ".join(values)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
