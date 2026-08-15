"""Collect recent Power BI learning videos from YouTube RSS feeds."""

from __future__ import annotations

import csv
import re
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT_DIR = Path(__file__).resolve().parents[1]
LEARNING_OUTPUT_PATH = ROOT_DIR / "docs" / "curation" / "powerbi_learning_videos" / "all.csv"
UPDATE_OUTPUT_PATH = ROOT_DIR / "docs" / "curation" / "powerbi_update_videos" / "all.csv"
PROGRAM_OUTPUT_PATH = ROOT_DIR / "docs" / "curation" / "powerbi_learning_programs" / "all.csv"
THUMBNAIL_DIR = ROOT_DIR / "folio_app" / "static" / "powerbi_learning_thumbs"
MAX_PER_CHANNEL = 3
MAX_ROWS = 30


@dataclass(frozen=True)
class Channel:
    name: str
    kind: str
    feed_url: str
    limit: int = MAX_PER_CHANNEL


CHANNELS = [
    Channel("Microsoft Power BI", "공식", "https://www.youtube.com/feeds/videos.xml?channel_id=UCy--PYvwBwAeuYaR8JLmrfg", limit=30),
    Channel("Guy in a Cube", "실무", "https://www.youtube.com/feeds/videos.xml?channel_id=UCFp1vaKzpfvoGai0vE5VJ0w"),
    Channel("How to Power BI", "디자인", "https://www.youtube.com/feeds/videos.xml?channel_id=UCcfngi7_ASuo5jdWX0bNauQ"),
    Channel("어니언 비아이 (ONION BI)", "한국 크리에이터", "https://www.youtube.com/feeds/videos.xml?channel_id=UCwRBy6O2Z0s9PHucNS-HHWQ", limit=6),
    Channel("SQLBI", "DAX", "https://www.youtube.com/feeds/videos.xml?user=sqlbit"),
    Channel("RADACAD", "모델링", "https://www.youtube.com/feeds/videos.xml?channel_id=UCsOfIwAXj1fT6LDqEDEAb4g"),
    Channel("Havens Consulting", "시각화", "https://www.youtube.com/feeds/videos.xml?channel_id=UCjlfQwqb-0S40XQ8seYPLSw"),
]

PROGRAM_PLAYLISTS = [
    {
        "title": "Analyze & Visualize Data with Power BI",
        "title_ko": "Analyze & Visualize Data with Power BI",
        "provider": "Microsoft Power BI",
        "program_type": "공식 학습 과정",
        "topic": "공식 학습",
        "summary_ko": "Power BI 입문자가 기본 개념, 데이터 분석, 시각화 흐름을 순서대로 학습할 수 있는 공식 플레이리스트입니다.",
        "playlist_url": "https://youtube.com/playlist?list=PL1N57mwBHtN0JFoKSR0n-tBkUJHeMP2cP",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PL1N57mwBHtN0JFoKSR0n-tBkUJHeMP2cP",
    },
    {
        "title": "Power BI Desktop Basics",
        "title_ko": "Power BI 데스크톱 기초 시리즈",
        "provider": "어니언 비아이 (ONION BI)",
        "program_type": "한국어 학습 과정",
        "topic": "한국 크리에이터",
        "summary_ko": "Power BI Desktop 입문자가 데이터 불러오기, 기본 가공, 보고서 제작 흐름을 순서대로 익히는 한국어 학습 시리즈입니다.",
        "playlist_url": "https://youtube.com/playlist?list=PLXTZTI9YjEQ1-HcDq36JGJZ5AjBmv6dcX",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PLXTZTI9YjEQ1-HcDq36JGJZ5AjBmv6dcX",
    },
    {
        "title": "Power BI Desktop Advanced",
        "title_ko": "Power BI 데스크톱 심화 시리즈",
        "provider": "어니언 비아이 (ONION BI)",
        "program_type": "한국어 학습 과정",
        "topic": "한국 크리에이터",
        "summary_ko": "모델링과 DAX 원리를 실습 중심으로 따라가며 Power BI 활용도를 높이는 심화 시리즈입니다.",
        "playlist_url": "https://youtube.com/playlist?list=PLXTZTI9YjEQ1166NsBJ9m1Z9g_P5K5abE",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PLXTZTI9YjEQ1166NsBJ9m1Z9g_P5K5abE",
    },
    {
        "title": "Power Query Series",
        "title_ko": "파워쿼리(Power Query) 시리즈",
        "provider": "어니언 비아이 (ONION BI)",
        "program_type": "한국어 학습 과정",
        "topic": "한국 크리에이터",
        "summary_ko": "Power Query로 데이터를 정리하고 변환하는 과정을 한국어로 학습할 수 있는 시리즈입니다.",
        "playlist_url": "https://youtube.com/playlist?list=PLXTZTI9YjEQ3bKE-Z0ntlWDEsimzpZqbI",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PLXTZTI9YjEQ3bKE-Z0ntlWDEsimzpZqbI",
    },
    {
        "title": "BI Specialist Practical Exam Prep",
        "title_ko": "경영정보시각화능력 실기 준비",
        "provider": "어니언 비아이 (ONION BI)",
        "program_type": "한국어 학습 과정",
        "topic": "한국 크리에이터",
        "summary_ko": "경영정보시각화능력 실기 준비를 Power BI 예제와 함께 따라갈 수 있는 시험 대비 시리즈입니다.",
        "playlist_url": "https://youtube.com/playlist?list=PLXTZTI9YjEQ399LuQAg_cCMWAxhAkEq_B",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PLXTZTI9YjEQ399LuQAg_cCMWAxhAkEq_B",
    },
    {
        "title": "Power BI Service Series",
        "title_ko": "Power BI 서비스 시리즈",
        "provider": "어니언 비아이 (ONION BI)",
        "program_type": "한국어 학습 과정",
        "topic": "한국 크리에이터",
        "summary_ko": "Power BI Service에서 공유, 게시, 협업 흐름을 이해하는 데 도움이 되는 한국어 시리즈입니다.",
        "playlist_url": "https://youtube.com/playlist?list=PLXTZTI9YjEQ3bEmc4vPSEhp_hMeltyfeI",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PLXTZTI9YjEQ3bEmc4vPSEhp_hMeltyfeI",
    },
    {
        "title": "Power BI DAX Functions",
        "title_ko": "Power BI DAX 함수 시리즈",
        "provider": "어니언 비아이 (ONION BI)",
        "program_type": "한국어 학습 과정",
        "topic": "한국 크리에이터",
        "summary_ko": "기초부터 중급까지 DAX 함수 사용법을 단계적으로 익히는 한국어 시리즈입니다.",
        "playlist_url": "https://youtube.com/playlist?list=PLXTZTI9YjEQ172Ek4eT7TJGK4WAEZ2YV5",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PLXTZTI9YjEQ172Ek4eT7TJGK4WAEZ2YV5",
    },
]


NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def main() -> None:
    rows = []
    for channel in CHANNELS:
        try:
            rows.extend(_fetch_channel(channel)[: channel.limit])
        except Exception as exc:
            print(f"Skipped {channel.name}: {exc}")
    rows = sorted(rows, key=lambda row: row["published_at"], reverse=True)
    update_rows = [row for row in rows if _is_official_update_video(row)]
    learning_rows = [row for row in rows if not _is_official_update_video(row)][:MAX_ROWS]
    program_rows = _collect_programs()
    _write_rows(LEARNING_OUTPUT_PATH, learning_rows)
    _write_rows(UPDATE_OUTPUT_PATH, update_rows)
    _write_program_rows(PROGRAM_OUTPUT_PATH, program_rows)
    print(f"Wrote {len(learning_rows)} rows to {LEARNING_OUTPUT_PATH.relative_to(ROOT_DIR)}")
    print(f"Wrote {len(update_rows)} rows to {UPDATE_OUTPUT_PATH.relative_to(ROOT_DIR)}")
    print(f"Wrote {len(program_rows)} rows to {PROGRAM_OUTPUT_PATH.relative_to(ROOT_DIR)}")


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "channel_name",
                "channel_type",
                "topic",
                "title_en",
                "title_ko",
                "summary_ko",
                "published_at",
                "video_url",
                "thumbnail_url",
                "thumbnail_asset",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_program_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "title",
                "title_ko",
                "provider",
                "program_type",
                "topic",
                "summary_ko",
                "playlist_url",
                "thumbnail_url",
                "thumbnail_asset",
                "video_count",
                "first_video_title",
                "first_video_url",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _collect_programs() -> list[dict[str, str]]:
    rows = []
    for playlist in PROGRAM_PLAYLISTS:
        try:
            entries = _fetch_playlist_entries(playlist["feed_url"])
        except Exception as exc:
            print(f"Skipped program {playlist['title']}: {exc}")
            entries = []
        first = entries[0] if entries else {}
        rows.append(
            {
                "title": playlist["title"],
                "title_ko": playlist["title_ko"],
                "provider": playlist["provider"],
                "program_type": playlist["program_type"],
                "topic": playlist["topic"],
                "summary_ko": playlist["summary_ko"],
                "playlist_url": playlist["playlist_url"],
                "thumbnail_url": first.get("thumbnail_url", ""),
                "thumbnail_asset": first.get("thumbnail_asset", ""),
                "video_count": str(len(entries)),
                "first_video_title": first.get("title", ""),
                "first_video_url": first.get("video_url", ""),
            }
        )
    return rows


def _fetch_playlist_entries(feed_url: str) -> list[dict[str, str]]:
    request = urllib.request.Request(feed_url, headers={"User-Agent": "folio-powerbi-curator/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        xml_text = response.read()
    root = ET.fromstring(xml_text)
    entries = []
    for entry in root.findall("atom:entry", NAMESPACES):
        video_id = _text(entry, "yt:videoId")
        title = _text(entry, "atom:title")
        media_group = entry.find("media:group", NAMESPACES)
        thumbnail_url = ""
        if media_group is not None:
            thumbnail = media_group.find("media:thumbnail", NAMESPACES)
            thumbnail_url = thumbnail.attrib.get("url", "") if thumbnail is not None else ""
        entries.append(
            {
                "title": title,
                "video_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
                "thumbnail_url": thumbnail_url,
                "thumbnail_asset": _download_thumbnail(video_id, thumbnail_url),
            }
        )
    return entries


def _fetch_channel(channel: Channel) -> list[dict[str, str]]:
    request = urllib.request.Request(channel.feed_url, headers={"User-Agent": "folio-powerbi-curator/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        xml_text = response.read()
    root = ET.fromstring(xml_text)
    rows = []
    for entry in root.findall("atom:entry", NAMESPACES):
        video_id = _text(entry, "yt:videoId")
        title = _text(entry, "atom:title")
        published_at = _text(entry, "atom:published")[:10]
        media_group = entry.find("media:group", NAMESPACES)
        thumbnail_url = ""
        if media_group is not None:
            thumbnail = media_group.find("media:thumbnail", NAMESPACES)
            thumbnail_url = thumbnail.attrib.get("url", "") if thumbnail is not None else ""
        thumbnail_asset = _download_thumbnail(video_id, thumbnail_url)
        rows.append(
            {
                "channel_name": channel.name,
                "channel_type": channel.kind,
                "topic": _topic_for(title, channel.kind),
                "title_en": title,
                "title_ko": _title_ko(title),
                "summary_ko": _summary_ko(title, channel.kind),
                "published_at": published_at,
                "video_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
                "thumbnail_url": thumbnail_url,
                "thumbnail_asset": thumbnail_asset,
            }
        )
    return rows


def _download_thumbnail(video_id: str, thumbnail_url: str) -> str:
    if not video_id or not thumbnail_url:
        return ""
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
    asset_name = f"powerbi_learning_thumbs/{video_id}.jpg"
    output_path = ROOT_DIR / "folio_app" / "static" / asset_name
    request = urllib.request.Request(thumbnail_url, headers={"User-Agent": "folio-powerbi-curator/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            image_bytes = response.read()
        with Image.open(BytesIO(image_bytes)) as image:
            image.convert("RGB").save(output_path, format="JPEG", quality=88, progressive=False)
    except Exception as exc:
        print(f"Skipped thumbnail {video_id}: {exc}")
        return ""
    return asset_name


def _text(element: ET.Element, selector: str) -> str:
    child = element.find(selector, NAMESPACES)
    return child.text.strip() if child is not None and child.text else ""


def _topic_for(title: str, fallback: str) -> str:
    text = title.lower()
    if "power bi update" in text:
        return "공식 업데이트"
    if fallback == "공식":
        return "공식 학습"
    if fallback == "한국 크리에이터":
        return "한국 크리에이터"
    if "dax" in text or "measure" in text:
        return "DAX"
    if "model" in text or "relationship" in text:
        return "모델링"
    if "design" in text or "visual" in text or "report" in text:
        return "시각화"
    if "fabric" in text or "copilot" in text:
        return "Fabric"
    if "power query" in text or "query" in text:
        return "Power Query"
    return fallback


def _title_ko(title: str) -> str:
    return _normalize_title(title)


def _summary_ko(title: str, channel_kind: str) -> str:
    topic = _topic_for(title, channel_kind)
    summary_by_topic = {
        "DAX": "DAX 계산식과 측정값 작성 방식을 익히는 데 참고할 수 있는 영상입니다.",
        "모델링": "관계, 모델 구조, 성능을 이해하는 데 도움이 되는 모델링 학습 영상입니다.",
        "시각화": "보고서 화면 구성과 시각적 표현을 개선하는 데 참고할 수 있는 영상입니다.",
        "Fabric": "Fabric과 Power BI의 최신 기능 흐름을 파악하는 데 도움이 되는 영상입니다.",
        "Power Query": "데이터 정리와 변환 과정을 이해하는 데 참고할 수 있는 영상입니다.",
        "한국 크리에이터": "한국어로 Power BI 실무 흐름을 익히는 데 참고할 수 있는 영상입니다.",
    }
    return summary_by_topic.get(topic, "Power BI 실무 학습에 참고할 수 있는 영상입니다.")


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def _is_official_update_video(row: dict[str, str]) -> bool:
    return row.get("channel_name") == "Microsoft Power BI" and "power bi update" in row.get("title_en", "").lower()


if __name__ == "__main__":
    main()
