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


DEFAULT_DOWNLOAD_URL = "https://www.microsoft.com/ko-kr/download/details.aspx?id=58494"
DEFAULT_OUTPUT_PATH = Path("docs/curation/powerbi_desktop_download/all.csv")

FIELDNAMES = [
    "source",
    "content_type",
    "title",
    "summary_ko",
    "source_url",
    "version",
    "published_at",
    "file_name",
    "file_size",
    "description_ko",
    "capabilities_ko",
    "image_urls",
    "tags",
    "publication_status",
    "collected_at",
]


def main() -> int:
    args = _parse_args()
    row = collect_powerbi_desktop_download(args.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(args.output, [row])
    print("Collected rows: 1")
    print(f"Version: {row.get('version')}")
    print(f"Published: {row.get('published_at')}")
    print(f"Saved: {args.output}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect the current Microsoft Power BI Desktop download metadata for FOLIO curation.",
    )
    parser.add_argument("--url", default=DEFAULT_DOWNLOAD_URL, help=f"Download URL. Defaults to {DEFAULT_DOWNLOAD_URL}.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"CSV output path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    return parser.parse_args()


def collect_powerbi_desktop_download(url: str = DEFAULT_DOWNLOAD_URL) -> dict[str, str]:
    page = _fetch_text(url)
    parser = _DownloadPageParser(url)
    parser.feed(page)
    parser.close()
    data = _extract_download_metadata(parser.nodes)
    capabilities = _extract_capabilities(parser.nodes)
    images = _extract_images(parser.nodes)
    title = data.get("title") or "Microsoft Power BI Desktop"
    version = data.get("version", "")
    published_at = data.get("published_at", "")
    file_name = data.get("file_name", "")
    file_size = data.get("file_size", "")
    description = data.get("description", "")

    return {
        "source": "Microsoft Download Center",
        "content_type": "powerbi_desktop_download",
        "title": title,
        "summary_ko": _summary_ko(version, published_at, file_name, file_size),
        "source_url": url,
        "version": version,
        "published_at": published_at,
        "file_name": file_name,
        "file_size": file_size,
        "description_ko": description,
        "capabilities_ko": " / ".join(capabilities),
        "image_urls": "; ".join(images),
        "tags": "Power BI; Power BI Desktop; PBIX; 다운로드; 웹 게시 준비",
        "publication_status": "review",
        "collected_at": datetime.now().replace(microsecond=0).isoformat(),
    }


def _fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "FOLIO Power BI Desktop download collector/0.1",
        },
    )
    with urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8")


class _DownloadPageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.nodes: list[dict[str, Any]] = []
        self._capture_tag = ""
        self._capture_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value or "" for name, value in attrs}
        if tag in {"h1", "h2", "h3", "p", "li"}:
            self._capture_tag = tag
            self._capture_text = []
            return
        if tag == "img" and attr.get("src"):
            self.nodes.append(
                {
                    "tag": "img",
                    "text": attr.get("alt", "").strip(),
                    "src": urljoin(self.base_url, attr["src"]),
                }
            )

    def handle_endtag(self, tag: str) -> None:
        if tag != self._capture_tag:
            return
        text = _normalize_space(" ".join(self._capture_text))
        if text:
            self.nodes.append({"tag": self._capture_tag, "text": text})
        self._capture_tag = ""
        self._capture_text = []

    def handle_data(self, data: str) -> None:
        if self._capture_tag:
            self._capture_text.append(data)


def _extract_download_metadata(nodes: list[dict[str, Any]]) -> dict[str, str]:
    texts = [node["text"] for node in nodes if node.get("text")]
    metadata = {
        "title": next((text for text in texts if text == "Microsoft Power BI Desktop"), "Microsoft Power BI Desktop"),
        "description": _description(texts),
        "version": _value_after_label(texts, "버전:"),
        "published_at": _value_after_label(texts, "Date Published:"),
        "file_name": _value_after_label(texts, "File Name:"),
        "file_size": _value_after_label(texts, "File Size:"),
    }
    if not metadata["version"]:
        metadata["version"] = _first_match(texts, r"\b\d+\.\d+\.\d+\.\d+\b")
    return metadata


def _description(texts: list[str]) -> str:
    for text in texts:
        if "Microsoft Power BI Desktop은 분석가용으로 빌드되었습니다" in text:
            return text
    return ""


def _value_after_label(texts: list[str], label: str) -> str:
    for index, text in enumerate(texts):
        if text == label:
            return texts[index + 1] if index + 1 < len(texts) else ""
        if text.startswith(label):
            return text.removeprefix(label).strip()
    return ""


def _first_match(texts: list[str], pattern: str) -> str:
    for text in texts:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ""


def _extract_capabilities(nodes: list[dict[str, Any]]) -> list[str]:
    capabilities = []
    known_starts = (
        "데이터 가져오기",
        "새 측정값",
        "보고서 만들기",
        "보고서 저장",
        "보고서 업로드 또는 게시",
    )
    for node in nodes:
        text = node.get("text", "")
        if any(text.startswith(marker) for marker in known_starts):
            capabilities.append(text)
    return capabilities


def _extract_images(nodes: list[dict[str, Any]], limit: int = 3) -> list[str]:
    urls = []
    for node in nodes:
        if node.get("tag") == "img" and node.get("src"):
            urls.append(node["src"])
        if len(urls) >= limit:
            break
    return urls


def _summary_ko(version: str, published_at: str, file_name: str, file_size: str) -> str:
    parts = ["Power BI Desktop 최신 다운로드 정보를 확인합니다."]
    if version:
        parts.append(f"현재 수집된 버전은 {version}입니다.")
    if published_at:
        parts.append(f"게시일은 {published_at}입니다.")
    if file_name:
        parts.append(f"설치 파일은 {file_name}입니다.")
    if file_size:
        parts.append(f"파일 크기는 {file_size}입니다.")
    parts.append("PBIX 보고서를 FOLIO에 웹 게시하기 전 준비 콘텐츠로 활용할 수 있습니다.")
    return " ".join(parts)


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
