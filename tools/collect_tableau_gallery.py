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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from folio_app.services.project_normalizers import clean_project_payload


DEFAULT_GALLERY_URL = "https://www.tableau.com/viz-gallery"
DEFAULT_OUTPUT_PATH = Path("docs/curation/tableau_gallery/all.csv")
DEFAULT_ADMIN_EMAIL = "admin@folio.com"

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
    "status",
    "details_title",
    "first_published",
    "last_published",
    "language",
    "embed_code",
    "registered_project_id",
]


def main() -> int:
    args = _parse_args()
    rows = collect_tableau_gallery(args)
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
        description="Collect Tableau Viz Gallery share-panel embed code into a FOLIO curation CSV.",
    )
    parser.add_argument("--url", default=DEFAULT_GALLERY_URL, help=f"Gallery URL. Defaults to {DEFAULT_GALLERY_URL}.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"CSV output path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    parser.add_argument("--wait-seconds", type=float, default=5.0, help="Seconds to wait on each viz detail page.")
    parser.add_argument("--share-wait-seconds", type=float, default=2.0, help="Seconds to wait after clicking Share.")
    parser.add_argument("--start-index", type=int, default=1, help="First 1-based gallery item index to collect.")
    parser.add_argument("--end-index", type=int, default=0, help="Last 1-based gallery item index to collect.")
    parser.add_argument(
        "--skip-index",
        type=int,
        action="append",
        default=[],
        help="1-based gallery item index to skip. May be repeated.",
    )
    parser.add_argument(
        "--only-index",
        type=int,
        action="append",
        default=[],
        help="Only collect this 1-based gallery item index. May be repeated.",
    )
    parser.add_argument("--force", action="store_true", help="Re-collect rows already present in the output CSV.")
    parser.add_argument("--headless", action="store_true", help="Run Chrome headless. Tableau may block headless runs.")
    parser.add_argument("--register", action="store_true", help="Insert collected rows into Supabase projects.")
    parser.add_argument(
        "--admin-email",
        default=DEFAULT_ADMIN_EMAIL,
        help=f"Admin account email for --register. Defaults to {DEFAULT_ADMIN_EMAIL}.",
    )
    return parser.parse_args()


def collect_tableau_gallery(args: argparse.Namespace) -> list[dict[str, str]]:
    existing_rows = _read_rows(args.output)
    rows_by_url = {row.get("source_url", ""): row for row in existing_rows if row.get("source_url")}
    output_rows: list[dict[str, str]] = []

    driver = webdriver.Chrome(options=_chrome_options(args.headless))
    try:
        links = _collect_gallery_links(driver, args.url, args.wait_seconds)
        print(f"Gallery links: {len(links)}")
        for index, source_url in enumerate(links, start=1):
            if not _should_collect_index(args, index):
                existing = rows_by_url.get(source_url)
                if existing:
                    output_rows.append(existing)
                continue

            existing = rows_by_url.get(source_url)
            if existing and not args.force:
                print(f"[{index}/{len(links)}] reuse {existing.get('status')} {existing.get('title')}")
                output_rows.append(existing)
                _write_rows(args.output, output_rows)
                continue

            print(f"[{index}/{len(links)}] collect {source_url}", flush=True)
            row = _collect_one(driver, index, source_url, args.url, args.wait_seconds, args.share_wait_seconds)
            print(f"    {row.get('status')} {row.get('title')}", flush=True)
            output_rows.append(row)
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
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return options


def _collect_gallery_links(driver: Any, gallery_url: str, wait_seconds: float) -> list[str]:
    driver.set_page_load_timeout(60)
    driver.get(gallery_url)
    time.sleep(wait_seconds)
    _accept_cookies(driver)

    links: list[str] = []
    seen: set[str] = set()
    selector = 'a[href*="public.tableau.com/app/profile/"][href*="/viz/"]'
    for anchor in driver.find_elements(By.CSS_SELECTOR, selector):
        href = anchor.get_attribute("href") or ""
        if href and href not in seen:
            seen.add(href)
            links.append(href)
    return links


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
    source_url: str,
    gallery_url: str,
    wait_seconds: float,
    share_wait_seconds: float,
) -> dict[str, str]:
    row = _base_row(index, source_url, gallery_url)
    try:
        driver.set_page_load_timeout(60)
        driver.get(source_url)
        time.sleep(wait_seconds)
        _accept_cookies(driver)

        title = _title_from_driver(driver)
        creator = _creator_from_body(driver, title, source_url)
        first_published, last_published, language = _dates_and_language_from_body(driver)
        row.update(
            {
                "title": title,
                "creator_name": creator,
                "creator_url": _creator_url_from_source(source_url),
                "details_title": title,
                "first_published": first_published,
                "last_published": last_published,
                "language": language,
            }
        )

        if "404" in title or "not found" in title.lower() or "찾을 수 없음" in title:
            row["status"] = "skipped_404"
            return row

        share_button = _find_share_button(driver)
        if share_button is None:
            row["status"] = "skipped_no_share_after_wait"
            return row

        driver.execute_script('arguments[0].scrollIntoView({block: "center"});', share_button)
        time.sleep(0.2)
        ActionChains(driver).move_to_element(share_button).click().perform()
        time.sleep(share_wait_seconds)

        embed_code, embed_url, thumbnail_url = _extract_share_fields_from_viz_frame(driver)
        row.update({"embed_code": embed_code, "embed_url": embed_url, "thumbnail_url": thumbnail_url})
        if embed_code and embed_url and thumbnail_url:
            row["status"] = "collected"
        else:
            row["status"] = _skip_status_for_missing_share_fields(embed_code, embed_url, thumbnail_url)
        return row
    except Exception as exc:
        row["status"] = f"error_{type(exc).__name__}"
        return row


def _base_row(index: int, source_url: str, gallery_url: str) -> dict[str, str]:
    return {
        "index": str(index),
        "title": "",
        "platform": "Tableau",
        "creator_name": "",
        "creator_url": "",
        "source_url": source_url,
        "embed_url": "",
        "thumbnail_url": "",
        "github_url": "",
        "categories": "Viz Gallery",
        "source_type": "curated",
        "embed_status": "unverified",
        "publication_status": "review",
        "weight": str(max(0, 1000000 - index * 10000)),
        "collected_from": gallery_url,
        "collected_category": "All",
        "collected_at": datetime.now().replace(microsecond=0).isoformat(),
        "status": "",
        "details_title": "",
        "first_published": "",
        "last_published": "",
        "language": "",
        "embed_code": "",
        "registered_project_id": "",
    }


def _accept_cookies(driver: Any) -> None:
    try:
        button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        if button.is_displayed():
            button.click()
            time.sleep(0.8)
    except Exception:
        pass


def _title_from_driver(driver: Any) -> str:
    title = (driver.title or "").strip()
    return re.sub(r"\s*\|\s*Tableau Public\s*$", "", title).strip() or title


def _creator_from_body(driver: Any, title: str, source_url: str) -> str:
    lines = [line.strip() for line in driver.find_element(By.TAG_NAME, "body").text.splitlines() if line.strip()]
    for position, line in enumerate(lines):
        if line == title and position + 2 < len(lines) and lines[position + 1].lower() in {"by", "작성자"}:
            return lines[position + 2]
    profile_match = re.search(r"/app/profile/([^/]+)/", source_url)
    return profile_match.group(1) if profile_match else "Tableau Public"


def _creator_url_from_source(source_url: str) -> str:
    profile_match = re.search(r"(https://public\.tableau\.com/app/profile/[^/]+)", source_url)
    return profile_match.group(1) if profile_match else ""


def _dates_and_language_from_body(driver: Any) -> tuple[str, str, str]:
    lines = [line.strip() for line in driver.find_element(By.TAG_NAME, "body").text.splitlines() if line.strip()]
    first_published = ""
    last_published = ""
    language = ""
    for line in lines:
        if line.startswith("First Published Date:"):
            first_published = line.split(":", 1)[1].strip()
        elif line.startswith("Last Published Date:"):
            last_published = line.split(":", 1)[1].strip()
        elif line in {"English (US)", "English"}:
            language = line
    return first_published, last_published, language


def _find_share_button(driver: Any) -> Any | None:
    for element in driver.find_elements(By.CSS_SELECTOR, 'button, [role="button"], div[role="button"]'):
        haystack = " ".join(
            [
                element.text or "",
                element.get_attribute("aria-label") or "",
                element.get_attribute("title") or "",
                element.get_attribute("class") or "",
            ]
        ).lower()
        if "share" in haystack or "공유" in haystack:
            return element
    return None


def _extract_share_fields_from_viz_frame(driver: Any) -> tuple[str, str, str]:
    for frame in driver.find_elements(By.TAG_NAME, "iframe"):
        frame_src = frame.get_attribute("src") or ""
        if "public.tableau.com/views/" not in frame_src:
            continue

        driver.switch_to.frame(frame)
        try:
            embed_code = ""
            embed_url = ""
            active_value = driver.execute_script(
                "const active = document.activeElement; return active && 'value' in active ? active.value : '';"
            )
            for candidate in [active_value or "", *_input_values(driver)]:
                if "viz_v1.js" in candidate:
                    embed_code = candidate
                elif candidate.startswith("https://public.tableau.com/views/"):
                    embed_url = candidate

            thumbnail_url = _static_image_from_embed_code(embed_code)
            return embed_code, embed_url, thumbnail_url
        finally:
            driver.switch_to.default_content()

    return "", "", ""


def _input_values(driver: Any) -> list[str]:
    values: list[str] = []
    for field in driver.find_elements(By.CSS_SELECTOR, "input, textarea"):
        values.append(field.get_attribute("value") or "")
    return values


def _static_image_from_embed_code(embed_code: str) -> str:
    match = re.search(r"<param name='static_image' value='([^']+)'", embed_code)
    if not match:
        return ""
    return html.unescape(match.group(1).replace("&#47;", "/"))


def _skip_status_for_missing_share_fields(embed_code: str, embed_url: str, thumbnail_url: str) -> str:
    missing = []
    if not embed_code:
        missing.append("embed_code")
    if not embed_url:
        missing.append("embed_url")
    if not thumbnail_url:
        missing.append("thumbnail")
    return "skipped_missing_" + "_".join(missing)


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
        if row.get("status") != "collected":
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
    title = row.get("title") or row.get("details_title") or "Untitled Tableau Viz"
    creator = row.get("creator_name") or "Tableau Public creator"
    first = row.get("first_published") or "Unknown"
    last = row.get("last_published") or "Unknown"
    language = row.get("language") or "Unknown"
    payload = clean_project_payload(
        {
            "title": title,
            "one_liner": f"Tableau Public Viz Gallery details item: {title} by {creator}.",
            "problem": _paragraph(f"Details title: {title}. Author: {creator}."),
            "dataset": _paragraph(
                f"First Published Date: {first}. Last Published Date: {last}. Language: {language}."
            ),
            "process": _paragraph(
                "This project was collected from the Tableau Public Viz Gallery. "
                "The embedded visualization and thumbnail were captured from the Tableau share panel's Embed Code field."
            ),
            "insights": _paragraph(
                "Use the Tableau Public Details metadata as the default introduction and report text for this curated item. "
                "Editorial summary and data-source notes can be expanded after manual review."
            ),
            "power_bi_url": row.get("embed_url", ""),
            "report_url": row.get("source_url", ""),
            "github_url": "",
            "thumbnail_url": row.get("thumbnail_url", ""),
            "tags": ["Tableau", "Viz Gallery", creator],
            "is_public": True,
        }
    )
    payload["author_id"] = author_id
    return payload


def _paragraph(value: str) -> str:
    return f"<p>{html.escape(value)}</p>"


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
