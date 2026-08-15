from __future__ import annotations

import argparse
import csv
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_RSS_URL = "https://community.fabric.microsoft.com/oxcrx34285/rss/board?board.id=community_blog"
DEFAULT_OUTPUT_PATH = Path("docs/curation/powerbi_community_blog/all.csv")
MAX_ITEMS = 30

FIELDNAMES = [
    "index",
    "source",
    "content_type",
    "title_en",
    "title_ko",
    "summary_en",
    "summary_ko",
    "source_url",
    "author",
    "published_at",
    "topic",
    "labels",
    "image_url",
    "publication_status",
    "collected_at",
]

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
}


def main() -> int:
    args = _parse_args()
    rows = collect_powerbi_community_blog(args.url, limit=args.limit, with_page_meta=args.with_page_meta)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(args.output, rows)
    print(f"Collected rows: {len(rows)}")
    print(f"Saved: {args.output}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Microsoft Power BI Community Blog posts for FOLIO curation.",
    )
    parser.add_argument("--url", default=DEFAULT_RSS_URL, help=f"RSS URL. Defaults to {DEFAULT_RSS_URL}.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help=f"CSV output path. Defaults to {DEFAULT_OUTPUT_PATH}.")
    parser.add_argument("--limit", type=int, default=MAX_ITEMS, help=f"Maximum posts to collect. Defaults to {MAX_ITEMS}.")
    parser.add_argument("--with-page-meta", action="store_true", help="Fetch each post page for labels and og:image metadata.")
    return parser.parse_args()


def collect_powerbi_community_blog(
    url: str = DEFAULT_RSS_URL,
    *,
    limit: int = MAX_ITEMS,
    with_page_meta: bool = False,
) -> list[dict[str, str]]:
    rss = _fetch_bytes(url)
    root = ET.fromstring(rss)
    items = root.findall("./channel/item")[:limit]
    rows = []
    collected_at = datetime.now().replace(microsecond=0).isoformat()
    for index, item in enumerate(items, start=1):
        title = _text(item, "title")
        summary = _html_to_text(_text(item, "description"))
        source_url = _text(item, "link")
        page_meta = _fetch_page_meta(source_url) if with_page_meta else {}
        labels = page_meta.get("labels") or _labels_for(title, summary)
        topic = _topic_for(title, summary, labels)
        rows.append(
            {
                "index": str(index),
                "source": "Microsoft Fabric Community",
                "content_type": "powerbi_community_blog",
                "title_en": title,
                "title_ko": _title_ko(title),
                "summary_en": summary,
                "summary_ko": _summary_ko(title, summary, topic),
                "source_url": source_url,
                "author": _text(item, "dc:creator"),
                "published_at": _date_value(_text(item, "dc:date") or _text(item, "pubDate")),
                "topic": topic,
                "labels": labels,
                "image_url": page_meta.get("image_url", ""),
                "publication_status": "review",
                "collected_at": collected_at,
            }
        )
    return sorted(rows, key=lambda row: row["published_at"], reverse=True)


def _fetch_page_meta(url: str) -> dict[str, str]:
    if not url:
        return {}
    try:
        page = _fetch_bytes(url).decode("utf-8", errors="replace")
    except Exception as exc:
        print(f"Skipped page metadata {url}: {exc}")
        return {}
    parser = _CommunityPostParser(url)
    parser.feed(page)
    parser.close()
    return {
        "labels": "; ".join(dict.fromkeys(parser.labels)),
        "image_url": parser.image_url,
    }


class _CommunityPostParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.image_url = ""
        self.labels: list[str] = []
        self._capture_label = False
        self._label_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value or "" for name, value in attrs}
        if tag == "meta" and not self.image_url:
            property_name = attr.get("property") or attr.get("name")
            if property_name in {"og:image", "twitter:image"} and attr.get("content"):
                self.image_url = urljoin(self.base_url, attr["content"])
        if tag == "a":
            href = attr.get("href", "")
            class_name = attr.get("class", "")
            if "label-name" in href or "label" in class_name.lower():
                self._capture_label = True
                self._label_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture_label:
            label = _normalize_space(" ".join(self._label_text))
            if label and label.lower() not in {"labels", "label"}:
                self.labels.append(label)
            self._capture_label = False
            self._label_text = []

    def handle_data(self, data: str) -> None:
        if self._capture_label:
            self._label_text.append(data)


def _fetch_bytes(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "FOLIO Power BI community curator/0.1",
        },
    )
    with urlopen(request, timeout=45) as response:
        return response.read()


def _text(element: ET.Element, selector: str) -> str:
    child = element.find(selector, NAMESPACES)
    return child.text.strip() if child is not None and child.text else ""


def _html_to_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return _normalize_space(text)


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def _date_value(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if "T" in value:
        return value[:10]
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return value


def _labels_for(title: str, summary: str) -> str:
    topic = _topic_for(title, summary, "")
    label_map = {
        "이벤트": "Events",
        "DAX": "How To; DAX",
        "Copilot": "How To; Copilot",
        "시각화": "Tips & Tricks; Visualizations",
        "모델링": "How To; Modeling",
        "Power Query": "How To; Power Query",
    }
    return label_map.get(topic, "How To")


def _topic_for(title: str, summary: str, labels: str) -> str:
    text = f"{title} {summary} {labels}".lower()
    if "contest" in text or "event" in text or "winner" in text or "champ" in text:
        return "이벤트"
    if "publish" in text or "publishing" in text or "refresh" in text or "power automate" in text or "service" in text:
        return "서비스 운영"
    if "copilot" in text or " ai " in f" {text} " or "prompt" in text:
        return "Copilot"
    if "dax" in text or "measure" in text or "calculation" in text:
        return "DAX"
    if "visual" in text or "chart" in text or "matrix" in text or "kpi" in text:
        return "시각화"
    if "query" in text or "power query" in text or "m language" in text:
        return "Power Query"
    if "semantic model" in text or "model" in text or "relationship" in text or "workspace" in text:
        return "모델링"
    return "실무 팁"


def _title_ko(title: str) -> str:
    normalized = _normalize_space(title)
    lower = normalized.lower()
    if "filter context" in lower and "dax udf" in lower:
        return "필터 컨텍스트를 재사용 가능한 DAX UDF 로직으로 바꾸는 방법"
    if "running total" in lower and "visual calculations" in lower:
        return "차트 하나에만 필요한 누계는 시각적 계산으로 처리할 수 있습니다"
    if "promptathon winners" in lower:
        return "SQL + AI Promptathon 수상자 발표"
    if "publishing explained" in lower:
        return "Power BI 게시 뒤에서 실제로 일어나는 구조"
    if "copilot custom instructions" in lower:
        return "Power BI Copilot 사용자 지정 지침으로 AI용 데이터 준비하기"
    if "dataviz world champs" in lower:
        return "Power BI Dataviz World Champs 소식"
    if "sticker challenge" in lower:
        return "Fabric Community Sticker Challenge 수상작"
    if "copilot set limits" in lower:
        return "Power BI Copilot이 참고할 데이터 범위 제한하기"
    if "matrix auto-expand" in lower:
        return "Power BI 행렬 자동 펼침 기능 활용하기"
    if "alerts with dax" in lower:
        return "Power Automate에서 DAX로 Power BI 알림 만들기"
    if "clone report" in lower:
        return "보고서를 다른 Lakehouse나 작업 영역으로 빠르게 연결하기"
    if "copilot accuracy" in lower:
        return "데이터 모델로 Power BI Copilot 정확도 높이기"
    if "dynamic formatting" in lower:
        return "동적 서식으로 KPI 단위와 스케일 제어하기"
    return _translate_terms(normalized)


def _summary_ko(title: str, summary: str, topic: str) -> str:
    text = f"{title} {summary}".lower()
    if "filter context" in text and "dax udf" in text:
        return "DAX 사용자 정의 함수로 반복되는 필터 컨텍스트 로직을 재사용하는 방법을 설명합니다."
    if "running total" in text and "visual calculations" in text:
        return "별도 측정값을 만들지 않고 특정 차트 안에서 누계나 이동평균을 처리하는 방법을 다룹니다."
    if "publishing" in text and "power bi service" in text:
        return "PBIX 게시 후 서비스에서 의미론적 모델, 보고서, 보안, 새로 고침이 어떻게 분리되어 관리되는지 설명합니다."
    if "copilot custom instructions" in text:
        return "업무 용어와 데이터 맥락을 Copilot이 더 잘 이해하도록 사용자 지정 지침을 설정하는 방법입니다."
    if "copilot set limits" in text:
        return "Copilot이 분석할 테이블과 열의 범위를 제한해 응답 품질과 보안을 조정하는 방법입니다."
    if "matrix auto-expand" in text:
        return "행렬 시각적 개체의 계층을 자동으로 펼쳐 사용자가 반복 클릭하지 않도록 만드는 기능을 소개합니다."
    if "power automate" in text and "dax" in text:
        return "DAX 쿼리 결과를 Power Automate로 보내 이메일이나 Teams 알림으로 활용하는 방법입니다."
    if "clone report" in text:
        return "Semantic Link Labs를 활용해 보고서 연결 대상을 새 Lakehouse나 작업 영역으로 빠르게 바꾸는 방법입니다."
    if "copilot accuracy" in text:
        return "Copilot이 데이터 모델을 더 정확히 해석하도록 모델 구조와 설명을 정리하는 실무 절차입니다."
    if "dynamic formatting" in text:
        return "사용자가 KPI 단위와 스케일을 유연하게 바꿀 수 있도록 동적 서식을 적용하는 방법입니다."
    if topic == "이벤트":
        return "Power BI 커뮤니티 이벤트, 대회, 수상자 발표 등 참여형 소식을 정리한 글입니다."
    if topic == "DAX":
        return "DAX 계산식, 측정값, 계산 컨텍스트를 실무 관점에서 이해하는 데 도움이 되는 글입니다."
    if topic == "Copilot":
        return "Power BI Copilot과 AI 기능을 실제 데이터 분석 흐름에 적용하는 방법을 다룹니다."
    if topic == "시각화":
        return "보고서 화면 구성과 시각적 개체 사용성을 개선하는 실무 팁입니다."
    if topic == "모델링":
        return "의미론적 모델, 관계, 작업 영역 구조를 이해하는 데 도움이 되는 글입니다."
    if topic == "서비스 운영":
        return "게시, 공유, 새로 고침, 자동화 등 Power BI Service 운영 흐름을 다룹니다."
    return _short_original_summary(summary)


def _translate_terms(value: str) -> str:
    replacements = {
        "Power BI": "Power BI",
        "Copilot": "Copilot",
        "Visual Calculations": "시각적 계산",
        "semantic model": "의미론적 모델",
        "Semantic Model": "의미론적 모델",
        "Publishing": "게시",
        "publishing": "게시",
        "DAX": "DAX",
        "Power Query": "Power Query",
        "Matrix": "행렬",
        "Running Total": "누계",
        "Custom Instructions": "사용자 지정 지침",
    }
    translated = value
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        translated = re.sub(re.escape(source), target, translated, flags=re.IGNORECASE)
    return translated


def _short_original_summary(value: str) -> str:
    text = _normalize_space(value)
    if len(text) > 150:
        text = text[:147].rsplit(" ", 1)[0] + "..."
    return f"원문 요약을 바탕으로 확인할 Power BI 커뮤니티 글입니다. {text}" if text else "Power BI 커뮤니티에서 공유된 최신 글입니다."


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
