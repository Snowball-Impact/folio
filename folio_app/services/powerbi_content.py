"""Curated Power BI content loading and shaping."""

from __future__ import annotations

import csv
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from folio_app.services.powerbi_i18n import (
    localize_date,
    localize_fix,
    localize_release_label,
    release_summary_bullet,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
CURATION_DIR = ROOT_DIR / "docs" / "curation"
DESKTOP_CSV = CURATION_DIR / "powerbi_desktop_download" / "all.csv"
UPDATES_CSV = CURATION_DIR / "powerbi_updates" / "all.csv"
CHANGELOG_CSV = CURATION_DIR / "powerbi_changelog" / "all.csv"
LEARNING_CSV = CURATION_DIR / "powerbi_learning_videos" / "all.csv"
UPDATE_VIDEOS_CSV = CURATION_DIR / "powerbi_update_videos" / "all.csv"
LEARNING_PROGRAMS_CSV = CURATION_DIR / "powerbi_learning_programs" / "all.csv"
COMMUNITY_BLOG_CSV = CURATION_DIR / "powerbi_community_blog" / "all.csv"


@dataclass(frozen=True)
class PowerBIContent:
    desktop_rows: list[dict[str, str]]
    update_rows: list[dict[str, str]]
    changelog_rows: list[dict[str, str]]
    learning_rows: list[dict[str, str]]
    update_video_rows: list[dict[str, str]]
    learning_program_rows: list[dict[str, str]]
    community_rows: list[dict[str, str]]


@dataclass(frozen=True)
class PowerBINewsItem:
    sort_date: datetime
    label: str
    title: str
    source_row: dict[str, str]
    bullets: list[str]
    video_row: dict[str, str] | None = None


def load_powerbi_content() -> PowerBIContent:
    return PowerBIContent(
        desktop_rows=read_csv(DESKTOP_CSV),
        update_rows=read_csv(UPDATES_CSV),
        changelog_rows=read_csv(CHANGELOG_CSV),
        learning_rows=read_csv(LEARNING_CSV),
        update_video_rows=read_csv(UPDATE_VIDEOS_CSV),
        learning_program_rows=read_csv(LEARNING_PROGRAMS_CSV),
        community_rows=read_csv(COMMUNITY_BLOG_CSV),
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def first_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    return rows[0] if rows else None


def community_groups(rows: list[dict[str, str]]) -> "OrderedDict[str, list[dict[str, str]]]":
    sorted_rows = sorted(rows, key=lambda row: row.get("published_at") or "", reverse=True)
    groups: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    groups["전체"] = sorted_rows
    topic_order = ["Copilot", "DAX", "서비스 운영", "시각화", "이벤트", "실무 팁"]
    for topic in topic_order:
        topic_rows = [row for row in sorted_rows if (row.get("topic") or "실무 팁") == topic]
        if topic_rows:
            groups[topic] = topic_rows
    for row in sorted_rows:
        topic = row.get("topic") or "실무 팁"
        if topic not in groups:
            groups[topic] = [candidate for candidate in sorted_rows if (candidate.get("topic") or "실무 팁") == topic]
    return groups


def learning_categories(rows: list[dict[str, str]]) -> "OrderedDict[str, list[dict[str, str]]]":
    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    category_order = ["공식 학습", "한국 크리에이터", "DAX", "Power Query", "모델링", "시각화", "Fabric", "실무", "디자인"]
    filtered = [
        row
        for row in rows
        if "power bi update" not in row.get("title_en", "").lower()
    ]
    for category in category_order:
        category_rows = [row for row in filtered if (row.get("topic") or row.get("channel_type")) == category]
        if category_rows:
            grouped[category] = category_rows
    for row in filtered:
        category = row.get("topic") or row.get("channel_type") or "기타"
        if any(row in values for values in grouped.values()):
            continue
        grouped.setdefault(category, []).append(row)
    return grouped


def programs_for_category(rows: list[dict[str, str]], category: str) -> list[dict[str, str]]:
    return [row for row in rows if (row.get("topic") or "") == category]


def build_news_items(
    update_rows: list[dict[str, str]],
    changelog_rows: list[dict[str, str]],
    update_video_rows: list[dict[str, str]],
) -> list[PowerBINewsItem]:
    items: list[PowerBINewsItem] = []
    video_by_release = _update_videos_by_release(update_video_rows)
    for release_label, rows in _group_by(update_rows, "release_label").items():
        overview = _find_overview(rows)
        version = _first_value(rows, "version")
        title = localize_release_label(release_label)
        if version:
            title = f"{title} · v{version}"
        items.append(
            PowerBINewsItem(
                sort_date=_release_sort_date(release_label),
                label="월간 정기 업데이트",
                title=title,
                source_row=overview or first_row(rows) or {},
                bullets=_release_summary_bullets(rows),
                video_row=video_by_release.get(_release_match_key(release_label)),
            )
        )

    for release_label, rows in _group_by(changelog_rows, "release_label").items():
        version = _first_value(rows, "version")
        released_at = _first_value(rows, "released_at")
        title_parts = [localize_release_label(release_label)]
        if version:
            title_parts.append(f"v{version}")
        if released_at:
            title_parts.append(localize_date(released_at))
        items.append(
            PowerBINewsItem(
                sort_date=_date_sort_value(released_at) or _release_sort_date(release_label),
                label="패치 로그",
                title=" · ".join(title_parts),
                source_row=first_row(rows) or {},
                bullets=_changelog_summary_bullets(rows),
            )
        )

    return sorted(items, key=lambda item: item.sort_date, reverse=True)


def youtube_thumbnail_url(row: dict[str, str]) -> str:
    thumbnail_url = row.get("thumbnail_url") or ""
    if thumbnail_url:
        return thumbnail_url
    video_url = row.get("video_url") or ""
    if "v=" not in video_url:
        return ""
    video_id = video_url.split("v=", 1)[1].split("&", 1)[0]
    return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""


def _group_by(rows: Iterable[dict[str, str]], key: str) -> "OrderedDict[str, list[dict[str, str]]]":
    groups: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in rows:
        label = row.get(key) or "기타"
        groups.setdefault(label, []).append(row)
    return groups


def _update_videos_by_release(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    videos: dict[str, dict[str, str]] = {}
    for row in rows:
        key = _release_match_key(row.get("title_en") or row.get("title_ko"))
        if key:
            videos[key] = row
    return videos


def _release_match_key(value: str | None) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("power bi update", "").replace("update", "")
    text = text.replace("-", " ").replace(":", " ")
    return " ".join(text.split())


def _find_overview(rows: list[dict[str, str]]) -> dict[str, str] | None:
    for row in rows:
        if (row.get("section") or "").lower() == "overview":
            return row
    return first_row(rows)


def _first_value(rows: list[dict[str, str]], key: str) -> str:
    for row in rows:
        value = row.get(key)
        if value:
            return value
    return ""


def _release_summary_bullets(rows: list[dict[str, str]]) -> list[str]:
    bullets: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if (row.get("section") or "").lower() == "overview":
            continue
        bullet = release_summary_bullet(row)
        if not bullet or bullet in seen:
            continue
        seen.add(bullet)
        bullets.append(bullet)
        if len(bullets) >= 5:
            break
    return bullets


def _changelog_summary_bullets(rows: list[dict[str, str]]) -> list[str]:
    bullets: list[str] = []
    seen: set[str] = set()
    for row in rows:
        bullet = localize_fix(row.get("fix_en"))
        if not bullet or bullet in seen:
            continue
        seen.add(bullet)
        bullets.append(bullet)
        if len(bullets) >= 5:
            break
    return bullets


def _release_sort_date(value: str | None) -> datetime:
    text = str(value or "").strip()
    month_numbers = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    year = _first_year(text)
    for month_name, month_number in month_numbers.items():
        if month_name in text and year:
            return datetime(year, month_number, 1)
    return datetime(year or 1900, 1, 1)


def _date_sort_value(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%m/%d/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    year = _first_year(text)
    if year:
        return datetime(year, 1, 1)
    return None


def _first_year(value: str) -> int | None:
    for token in value.replace(",", " ").split():
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None
