from __future__ import annotations

from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse

from folio_app.services.project_content import sanitize_project_html


def clean_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if "title" in payload:
        data["title"] = payload.get("title", "").strip()
    if "one_liner" in payload:
        data["one_liner"] = payload.get("one_liner", "").strip() or None
    if "problem" in payload:
        data["problem"] = sanitize_project_html(payload.get("problem"))
    if "dataset" in payload:
        data["dataset"] = sanitize_project_html(payload.get("dataset")) or None
    if "process" in payload:
        data["process"] = sanitize_project_html(payload.get("process")) or None
    if "insights" in payload:
        data["insights"] = sanitize_project_html(payload.get("insights"))
    if "power_bi_url" in payload:
        data["power_bi_url"] = normalize_power_bi_embed_url(payload.get("power_bi_url", ""))
    if "report_url" in payload:
        data["report_url"] = normalize_optional_url(payload.get("report_url", ""))
    if "github_url" in payload:
        data["github_url"] = normalize_optional_url(payload.get("github_url", ""))
    if "thumbnail_url" in payload:
        data["thumbnail_url"] = normalize_optional_url(payload.get("thumbnail_url", ""))
    if "tags" in payload:
        data["tags"] = normalize_tags(payload.get("tags", ""))
    if "is_public" in payload:
        data["is_public"] = bool(payload.get("is_public"))
    return data


def normalize_tags(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        raw_tags = value
    else:
        raw_tags = value.replace("#", "").split(",")

    tags = []
    for tag in raw_tags:
        normalized = str(tag).strip()
        if normalized and normalized not in tags:
            tags.append(normalized)
    return tags[:10]


def normalize_optional_url(value: str | None) -> str | None:
    raw_value = (value or "").strip()
    if not raw_value:
        return None

    parsed = urlparse(raw_value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return raw_value
    return None


def normalize_power_bi_embed_url(value: str | None) -> str | None:
    raw_value = (value or "").strip()
    if not raw_value:
        return None

    if raw_value.lower().startswith("<iframe"):
        parser = _IframeSrcParser()
        parser.feed(raw_value)
        raw_value = parser.src or raw_value

    parsed = urlparse(raw_value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return raw_value
    return None


class _IframeSrcParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.src: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "iframe":
            return

        for name, value in attrs:
            if name.lower() == "src" and value:
                self.src = value.strip()
                return

