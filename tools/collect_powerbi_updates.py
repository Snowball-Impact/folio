from __future__ import annotations

import argparse
import csv
import html
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_ARCHIVE_URL = "https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-latest-update-archive?tabs=powerbi-desktop"
DEFAULT_OUTPUT_PATH = Path("docs/curation/powerbi_updates/all.csv")

FIELDNAMES = [
    "index",
    "source",
    "content_type",
    "title_en",
    "title_ko",
    "summary_en",
    "summary_ko",
    "source_url",
    "source_anchor",
    "release_label",
    "version",
    "section",
    "feature_title_en",
    "feature_title_ko",
    "feature_description_en",
    "feature_description_ko",
    "image_urls",
    "tags",
    "publication_status",
    "collected_at",
]


def main() -> int:
    args = _parse_args()
    rows = collect_powerbi_update_archive(args.url, max_releases=args.max_releases, since_year=args.since_year)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(args.output, rows)
    print(f"Collected rows: {len(rows)}")
    print(f"Saved: {args.output}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Power BI monthly update metadata for FOLIO curation.",
    )
    parser.add_argument("--url", default=DEFAULT_ARCHIVE_URL, help=f"Archive URL. Defaults to {DEFAULT_ARCHIVE_URL}.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"CSV output path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    parser.add_argument("--max-releases", type=int, default=0, help="Collect at most N monthly update sections. 0 means no limit.")
    parser.add_argument("--since-year", type=int, default=2025, help="Collect update sections from this year onward.")
    return parser.parse_args()


def collect_powerbi_update_archive(
    url: str = DEFAULT_ARCHIVE_URL,
    *,
    max_releases: int = 0,
    since_year: int = 2025,
) -> list[dict[str, str]]:
    page = _fetch_text(url)
    parser = _LearnArticleParser(url)
    parser.feed(page)
    parser.close()

    releases = _release_blocks(parser.article_nodes, max_releases=max_releases, since_year=since_year)
    rows: list[dict[str, str]] = []
    for release in releases:
        rows.extend(_rows_from_release(release, len(rows) + 1, source_base_url=url))
    return rows


def _fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "FOLIO Power BI curation collector/0.1",
        },
    )
    with urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8")


class _LearnArticleParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.article_nodes: list[dict[str, Any]] = []
        self._capture_tag = ""
        self._capture_attrs: dict[str, str] = {}
        self._capture_text: list[str] = []
        self._in_main = False
        self._current_link = ""
        self._in_row = False
        self._row_cells: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value or "" for name, value in attrs}
        if tag == "main" or attr.get("role") == "main":
            self._in_main = True

        if not self._in_main:
            return

        if tag == "tr":
            self._in_row = True
            self._row_cells = []
            return

        if tag in {"h2", "h3", "p", "li"} or (self._in_row and tag in {"td", "th"}):
            self._capture_tag = tag
            self._capture_attrs = attr
            self._capture_text = []
        elif tag == "a" and attr.get("href"):
            self._current_link = urljoin(self.base_url, attr["href"])
        elif tag == "img" and attr.get("src"):
            self.article_nodes.append(
                {
                    "tag": "img",
                    "text": attr.get("alt", "").strip(),
                    "src": urljoin(self.base_url, attr["src"]),
                }
            )

    def handle_endtag(self, tag: str) -> None:
        if tag == "main":
            self._in_main = False
        if not self._in_main:
            return
        if tag == "tr":
            if self._row_cells:
                self.article_nodes.append(
                    {
                        "tag": "tr",
                        "cells": list(self._row_cells),
                    }
                )
            self._in_row = False
            self._row_cells = []
            return
        if tag == "a":
            self._current_link = ""
        if tag == self._capture_tag:
            text = _normalize_space(" ".join(self._capture_text))
            if text:
                if self._in_row and self._capture_tag in {"td", "th"}:
                    self._row_cells.append(text)
                    self._capture_tag = ""
                    self._capture_attrs = {}
                    self._capture_text = []
                    return
                node = {
                    "tag": self._capture_tag,
                    "text": text,
                    "id": self._capture_attrs.get("id", ""),
                }
                if self._current_link:
                    node["href"] = self._current_link
                self.article_nodes.append(node)
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
        if node.get("tag") == "h2" and _is_update_heading(node.get("text", "")):
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


def _is_update_heading(value: str) -> bool:
    return bool(re.search(r"\bupdate\s*\(version\s+[\d.]+\)", value, flags=re.IGNORECASE))


def _year_from_text(value: str) -> int | None:
    match = re.search(r"\b(20\d{2})\b", value)
    return int(match.group(1)) if match else None


def _rows_from_release(release: dict[str, Any], start_index: int, *, source_base_url: str) -> list[dict[str, str]]:
    release_label, version = _parse_release_heading(release["heading"])
    source_url = _source_url(release["anchor"], source_base_url)
    summary = _first_paragraph(release["nodes"])
    images = _image_urls(release["nodes"])
    feature_rows = _feature_rows(release["nodes"])

    rows: list[dict[str, str]] = []
    overview_feature = {
        "section": "Overview",
        "feature": f"{release_label} overview",
        "description": summary,
    }
    for offset, feature in enumerate([overview_feature, *feature_rows]):
        title_en = f"Power BI {release_label}: {feature['feature']}"
        title_ko = _translate_title(title_en)
        description_en = feature["description"]
        rows.append(
            {
                "index": str(start_index + offset),
                "source": "Microsoft Learn",
                "content_type": "powerbi_update",
                "title_en": title_en,
                "title_ko": title_ko,
                "summary_en": summary,
                "summary_ko": _summarize_update_ko(release_label, feature["feature"], description_en),
                "source_url": source_url,
                "source_anchor": release["anchor"],
                "release_label": release_label,
                "version": version,
                "section": feature["section"],
                "feature_title_en": feature["feature"],
                "feature_title_ko": _translate_title(feature["feature"]),
                "feature_description_en": description_en,
                "feature_description_ko": _translate_description(description_en),
                "image_urls": "; ".join(images),
                "tags": _tags_for_feature(feature["section"], feature["feature"], description_en),
                "publication_status": "review",
                "collected_at": datetime.now().replace(microsecond=0).isoformat(),
            }
        )
    return rows


def _parse_release_heading(value: str) -> tuple[str, str]:
    match = re.match(r"(.+?)\s*\(version\s+([^)]+)\)", value, flags=re.IGNORECASE)
    if not match:
        return value, ""
    return match.group(1).strip(), match.group(2).strip()


def _source_url(anchor: str, base_url: str) -> str:
    if not anchor:
        return base_url
    return f"{base_url}#{anchor}"


def _first_paragraph(nodes: list[dict[str, Any]]) -> str:
    for node in nodes:
        if node.get("tag") == "p" and len(node.get("text", "")) > 40:
            return node["text"]
    return ""


def _image_urls(nodes: list[dict[str, Any]], limit: int = 3) -> list[str]:
    urls = []
    for node in nodes:
        if node.get("tag") == "img" and node.get("src"):
            urls.append(node["src"])
        if len(urls) >= limit:
            break
    return urls


def _feature_rows(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current_section = "General"
    cells: list[str] = []
    for node in nodes:
        tag = node.get("tag")
        text = node.get("text", "")
        if tag == "h3":
            current_section = text
            cells = []
            continue
        if tag == "tr":
            row_cells = [cell for cell in node.get("cells", []) if cell]
            if len(row_cells) < 2:
                continue
            if row_cells[0].lower() == "feature" or row_cells[1].lower() == "description":
                continue
            rows.append(
                {
                    "section": current_section,
                    "feature": row_cells[0],
                    "description": row_cells[1],
                }
            )
    return _dedupe_features(rows)


def _dedupe_features(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    unique = []
    for row in rows:
        key = (row["section"], row["feature"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def _translate_title(value: str) -> str:
    translated = value
    replacements = {
        "Power BI": "Power BI",
        "Generally Available": "정식 제공",
        "semantic models": "의미론적 모델",
        "semantic model": "의미론적 모델",
        "Data connectivity": "데이터 연결",
        "update": "업데이트",
        "General": "일반",
        "Reporting": "보고서 작성",
        "Modeling": "모델링",
        "Visualizations": "시각화",
        "Copilot": "Copilot",
        "Preview": "미리 보기",
        "Embedded": "임베디드",
        "visuals": "시각적 요소",
        "reports": "보고서",
    }
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        translated = re.sub(re.escape(source), target, translated, flags=re.IGNORECASE)
    return translated


def _translate_description(value: str) -> str:
    if not value:
        return ""
    return _summarize_sentence_ko(value)


def _summarize_update_ko(release_label: str, feature: str, description: str) -> str:
    translated_feature = _translate_title(feature)
    summary = _summarize_sentence_ko(description)
    if summary:
        return f"{release_label} Power BI 업데이트의 '{translated_feature}' 항목입니다. {summary}"
    return f"{release_label} Power BI 업데이트에서 '{translated_feature}' 항목을 확인하세요."


def _summarize_sentence_ko(value: str) -> str:
    normalized = _normalize_space(value)
    if not normalized:
        return ""
    shortened = normalized
    if len(shortened) > 220:
        shortened = shortened[:217].rsplit(" ", 1)[0] + "..."
    return f"원문 요약: {shortened}"


def _tags_for_feature(section: str, feature: str, description: str) -> str:
    tags = ["Power BI", "Power BI 업데이트", section]
    text = f"{feature} {description}".lower()
    if "copilot" in text or "ai" in text:
        tags.append("AI")
    if "embed" in text:
        tags.append("Embedded")
    if "visual" in text or "chart" in text:
        tags.append("시각화")
    if "model" in text or "dax" in text:
        tags.append("모델링")
    if "connector" in text or "data source" in text:
        tags.append("데이터 연결")
    return "; ".join(dict.fromkeys(tag for tag in tags if tag))


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
