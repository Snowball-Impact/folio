from __future__ import annotations

import re
from typing import Any


HTTP_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
MAX_TITLE_LENGTH = 120
MAX_ONE_LINER_LENGTH = 180


def clean_project_payload(raw: dict[str, Any]) -> dict[str, Any]:
    tags = raw.get("tags") or []
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",")]
    normalized_tags = list(dict.fromkeys(str(tag).strip() for tag in tags if str(tag).strip()))

    return {
        "title": str(raw.get("title") or "Untitled Project").strip()[:MAX_TITLE_LENGTH],
        "one_liner": str(raw.get("one_liner") or "").strip()[:MAX_ONE_LINER_LENGTH],
        "problem": str(raw.get("problem") or "").strip(),
        "dataset": str(raw.get("dataset") or "").strip(),
        "process": str(raw.get("process") or "").strip(),
        "insights": str(raw.get("insights") or "").strip(),
        "power_bi_url": _safe_url(raw.get("power_bi_url")),
        "report_url": _safe_url(raw.get("report_url")),
        "github_url": _safe_url(raw.get("github_url")),
        "thumbnail_url": _safe_url(raw.get("thumbnail_url")),
        "tags": normalized_tags,
        "is_public": bool(raw.get("is_public")),
    }


def _safe_url(value: Any) -> str:
    text = str(value or "").strip()
    return text if not text or HTTP_URL_RE.match(text) else ""
