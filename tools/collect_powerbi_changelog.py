from __future__ import annotations

import argparse
import csv
import html
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


DEFAULT_CHANGELOG_URL = "https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-change-log"
DEFAULT_OUTPUT_PATH = Path("docs/curation/powerbi_changelog/all.csv")

FIELDNAMES = [
    "index",
    "source",
    "content_type",
    "release_label",
    "version",
    "released_at",
    "fix_en",
    "summary_ko",
    "source_url",
    "source_anchor",
    "tags",
    "publication_status",
    "collected_at",
]


def main() -> int:
    args = _parse_args()
    rows = collect_powerbi_changelog(args.url, max_releases=args.max_releases, since_year=args.since_year)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(args.output, rows)
    print(f"Collected rows: {len(rows)}")
    print(f"Saved: {args.output}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Power BI Desktop change log fixes for FOLIO curation.",
    )
    parser.add_argument("--url", default=DEFAULT_CHANGELOG_URL, help=f"Change log URL. Defaults to {DEFAULT_CHANGELOG_URL}.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"CSV output path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    parser.add_argument("--max-releases", type=int, default=0, help="Collect at most N QFE release sections. 0 means no limit.")
    parser.add_argument("--since-year", type=int, default=2025, help="Collect QFE sections from this year onward.")
    return parser.parse_args()


def collect_powerbi_changelog(
    url: str = DEFAULT_CHANGELOG_URL,
    *,
    max_releases: int = 0,
    since_year: int = 2025,
) -> list[dict[str, str]]:
    page = _fetch_text(url)
    parser = _ChangeLogParser()
    parser.feed(page)
    parser.close()
    releases = _release_blocks(parser.nodes, max_releases=max_releases, since_year=since_year)
    rows: list[dict[str, str]] = []
    for release in releases:
        rows.extend(_rows_from_release(release, len(rows) + 1, base_url=url))
    return rows


def _fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "FOLIO Power BI changelog collector/0.1",
        },
    )
    with urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8")


class _ChangeLogParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.nodes: list[dict[str, Any]] = []
        self._in_main = False
        self._capture_tag = ""
        self._capture_attrs: dict[str, str] = {}
        self._capture_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value or "" for name, value in attrs}
        if tag == "main" or attr.get("role") == "main":
            self._in_main = True
        if not self._in_main:
            return
        if tag in {"h2", "p", "li"}:
            self._capture_tag = tag
            self._capture_attrs = attr
            self._capture_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "main":
            self._in_main = False
        if not self._in_main:
            return
        if tag != self._capture_tag:
            return
        text = _normalize_space(" ".join(self._capture_text))
        if text:
            self.nodes.append(
                {
                    "tag": self._capture_tag,
                    "text": text,
                    "id": self._capture_attrs.get("id", ""),
                }
            )
        self._capture_tag = ""
        self._capture_attrs = {}
        self._capture_text = []

    def handle_data(self, data: str) -> None:
        if self._capture_tag:
            self._capture_text.append(data)


def _release_blocks(nodes: list[dict[str, Any]], *, max_releases: int, since_year: int) -> list[dict[str, Any]]:
    releases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for node in nodes:
        if node.get("tag") == "h2" and "QFE" in node.get("text", ""):
            if current:
                releases.append(current)
                if max_releases and len(releases) >= max_releases:
                    return releases
            heading_year = _year_from_text(node.get("text", ""))
            if heading_year and heading_year < since_year:
                current = None
                break
            current = {
                "heading": node.get("text", ""),
                "anchor": node.get("id", ""),
                "nodes": [],
            }
            continue
        if current is not None:
            current["nodes"].append(node)
    if current and (not max_releases or len(releases) < max_releases):
        releases.append(current)
    return releases


def _year_from_text(value: str) -> int | None:
    match = re.search(r"\b(20\d{2})\b", value)
    return int(match.group(1)) if match else None


def _rows_from_release(release: dict[str, Any], start_index: int, *, base_url: str) -> list[dict[str, str]]:
    version, released_at = _parse_release_meta(release["nodes"])
    fixes = [node["text"] for node in release["nodes"] if node.get("tag") == "li" and _is_fix_item(node["text"])]
    source_url = f"{base_url}#{release['anchor']}" if release.get("anchor") else base_url
    rows = []
    for offset, fix in enumerate(fixes):
        rows.append(
            {
                "index": str(start_index + offset),
                "source": "Microsoft Learn",
                "content_type": "powerbi_changelog",
                "release_label": release["heading"],
                "version": version,
                "released_at": released_at,
                "fix_en": fix,
                "summary_ko": _summary_ko(release["heading"], version, released_at, fix),
                "source_url": source_url,
                "source_anchor": release.get("anchor", ""),
                "tags": _tags_for_fix(fix),
                "publication_status": "review",
                "collected_at": datetime.now().replace(microsecond=0).isoformat(),
            }
        )
    return rows


def _parse_release_meta(nodes: list[dict[str, Any]]) -> tuple[str, str]:
    for node in nodes:
        if node.get("tag") != "p":
            continue
        text = node.get("text", "")
        version_match = re.search(r"Version\s+([\d.]+)", text, flags=re.IGNORECASE)
        released_match = re.search(r"Released:\s*(.+)$", text, flags=re.IGNORECASE)
        if version_match:
            return version_match.group(1), released_match.group(1).strip() if released_match else ""
    return "", ""


def _is_fix_item(value: str) -> bool:
    if not value:
        return False
    lowered = value.lower()
    return any(marker in lowered for marker in ("fixed", "addressed", "resolved", "reverted", "correctly categorized", "feature update"))


def _summary_ko(release_label: str, version: str, released_at: str, fix: str) -> str:
    parts = [f"{release_label} 변경 로그 항목입니다."]
    if version:
        parts.append(f"버전 {version}.")
    if released_at:
        parts.append(f"릴리스일 {released_at}.")
    parts.append(f"원문 요약: {_shorten(fix)}")
    return " ".join(parts)


def _tags_for_fix(fix: str) -> str:
    lowered = fix.lower()
    tags = ["Power BI", "Power BI Desktop", "변경 로그", "버그 수정"]
    if "copilot" in lowered:
        tags.append("Copilot")
    if "directquery" in lowered:
        tags.append("DirectQuery")
    if "snowflake" in lowered:
        tags.append("Snowflake")
    if "visual" in lowered or "chart" in lowered:
        tags.append("시각화")
    if "model" in lowered or "measure" in lowered or "relationship" in lowered:
        tags.append("모델링")
    if "refresh" in lowered:
        tags.append("새로 고침")
    if "save" in lowered:
        tags.append("저장")
    return "; ".join(dict.fromkeys(tags))


def _shorten(value: str, limit: int = 220) -> str:
    value = _normalize_space(value)
    if len(value) <= limit:
        return value
    return value[: limit - 3].rsplit(" ", 1)[0] + "..."


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
