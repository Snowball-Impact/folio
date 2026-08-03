from __future__ import annotations

import argparse
import csv
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


DEFAULT_GALLERY_URL = "https://streamlit.io/gallery"
DEFAULT_OUTPUT_PATH = Path("docs/curation/streamlit_gallery/all.csv")


def main() -> int:
    args = _parse_args()
    apps = collect_streamlit_gallery(args.url)
    if args.category:
        apps = [
            app
            for app in apps
            if args.category in app.get("categories", [])
        ]

    rows = [_csv_row(app, args.url, args.category or "All") for app in apps]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(args.output, rows)

    print(f"Collected: {len(rows)}")
    print(f"Saved: {args.output}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Streamlit App Gallery metadata into a FOLIO curation CSV.",
    )
    parser.add_argument("--url", default=DEFAULT_GALLERY_URL, help=f"Gallery URL. Defaults to {DEFAULT_GALLERY_URL}.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"CSV output path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    parser.add_argument(
        "--category",
        default="",
        help="Optional exact Streamlit category filter, for example Favorites or Data visualization.",
    )
    return parser.parse_args()


def collect_streamlit_gallery(url: str = DEFAULT_GALLERY_URL) -> list[dict[str, Any]]:
    page = _fetch_text(url)
    data = _extract_next_data(page)
    page_props = data.get("props", {}).get("pageProps", {})
    apps = page_props.get("appsData") or page_props.get("allAppsData") or []
    return [app for app in apps if app.get("enabled") is True]


def _fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "FOLIO curation metadata collector/0.1",
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _extract_next_data(page: str) -> dict[str, Any]:
    match = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        page,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError("Could not find __NEXT_DATA__ in Streamlit Gallery page.")
    return json.loads(html.unescape(match.group(1)))


def _csv_row(app: dict[str, Any], collected_from: str, collected_category: str) -> dict[str, Any]:
    source_url = str(app.get("appUrl") or "").strip()
    categories = [str(category).strip() for category in app.get("categories") or [] if str(category).strip()]
    return {
        "title": app.get("title") or "",
        "platform": "Streamlit",
        "creator_name": app.get("author") or "",
        "creator_url": app.get("socialUrl") or "",
        "source_url": source_url,
        "embed_url": _streamlit_embed_url(source_url),
        "thumbnail_url": app.get("image") or "",
        "github_url": app.get("gitHubUrl") or "",
        "categories": "; ".join(categories),
        "source_type": "curated",
        "embed_status": "unverified",
        "publication_status": "review",
        "weight": app.get("weight") or 0,
        "collected_from": collected_from,
        "collected_category": collected_category,
        "collected_at": datetime.now().replace(microsecond=0).isoformat(),
    }


def _streamlit_embed_url(source_url: str) -> str:
    if not source_url:
        return ""
    if re.search(r"[?&]embed=true(?:&|$)", source_url):
        return source_url
    separator = "&" if "?" in source_url else "?"
    return f"{source_url}{separator}embed=true"


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
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
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
