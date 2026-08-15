"""Power BI news and update hub."""

from __future__ import annotations

import csv
import html
import math
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import streamlit as st

from folio_app.components.assets import static_image_src

ROOT_DIR = Path(__file__).resolve().parents[2]
CURATION_DIR = ROOT_DIR / "docs" / "curation"
DESKTOP_CSV = CURATION_DIR / "powerbi_desktop_download" / "all.csv"
UPDATES_CSV = CURATION_DIR / "powerbi_updates" / "all.csv"
CHANGELOG_CSV = CURATION_DIR / "powerbi_changelog" / "all.csv"
NEWS_PAGE_SIZE = 10


@dataclass(frozen=True)
class PowerBINewsItem:
    sort_date: datetime
    label: str
    title: str
    source_row: dict[str, str]
    bullets: list[str]


def render() -> None:
    desktop_rows = _read_csv(DESKTOP_CSV)
    update_rows = _read_csv(UPDATES_CSV)
    changelog_rows = _read_csv(CHANGELOG_CSV)

    _render_hero(_first(desktop_rows))
    _render_news_board(update_rows, changelog_rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _render_hero(desktop_row: dict[str, str] | None) -> None:
    logo_src = static_image_src("reference-powerbi-logo-cropped.webp")
    download_url = desktop_row.get("source_url") if desktop_row else ""
    cta_html = ""
    if download_url:
        cta_html = (
            '<a class="folio-powerbi-hero-cta" '
            f'href="{html.escape(download_url, quote=True)}" target="_blank" rel="noopener">'
            "최신 DESKTOP 다운로드"
            "</a>"
        )
    st.markdown(
        f"""
        <section class="folio-powerbi-hero-shell">
            <div class="folio-powerbi-hero">
                <div>
                    <div class="folio-powerbi-eyebrow">Power BI News</div>
                    <h1>Power BI 소식</h1>
                    <p>
                        Power BI 분석가에게 필요한 Desktop 다운로드, 월간 기능 업데이트,<br>
                        변경 로그를 원문 링크와 함께 모아 번역 및 요약합니다.
                    </p>
                    {cta_html}
                </div>
                <div class="folio-powerbi-hero-visual" aria-label="Power BI">
                    <img src="{logo_src}" alt="Power BI" />
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_news_board(update_rows: list[dict[str, str]], changelog_rows: list[dict[str, str]]) -> None:
    items = _build_news_items(update_rows, changelog_rows)
    if not items:
        _render_empty("아직 수집된 Power BI 소식이 없습니다.")
        return

    page_index, total_pages = _current_board_page(len(items))
    start = page_index * NEWS_PAGE_SIZE
    end = start + NEWS_PAGE_SIZE
    for index, item in enumerate(items[start:end], start=start + 1):
        _render_news_item(len(items) - index + 1, item)
    _render_pagination(page_index, total_pages)


def _render_news_item(index: int, item: PowerBINewsItem) -> None:
    st.markdown(
        f"""
        <details class="folio-powerbi-release-row">
            <summary>
                <span class="folio-powerbi-row-index">{index}</span>
                <span class="folio-powerbi-row-label">{_escape(item.label)}</span>
                <span class="folio-powerbi-expander-title">{_escape(item.title)}</span>
                {_source_link(item.source_row, label="원문")}
            </summary>
            <div class="folio-powerbi-release-body">
                {_summary_bullets_html(item.bullets)}
            </div>
        </details>
        """,
        unsafe_allow_html=True,
    )

def _render_empty(message: str) -> None:
    st.markdown(f'<div class="folio-powerbi-empty">{_escape(message)}</div>', unsafe_allow_html=True)


def _current_board_page(item_count: int) -> tuple[int, int]:
    total_pages = max(math.ceil(item_count / NEWS_PAGE_SIZE), 1)
    current = int(st.session_state.get("powerbi_news_page", 0))
    current = min(max(current, 0), total_pages - 1)
    st.session_state["powerbi_news_page"] = current
    return current, total_pages


def _render_pagination(page_index: int, total_pages: int) -> None:
    if total_pages <= 1:
        return
    _, previous_col, page_col, next_col, _ = st.columns([1, 0.08, 0.14, 0.08, 1])
    with previous_col:
        if st.button("←", key="powerbi_news_prev", disabled=page_index <= 0, use_container_width=True):
            st.session_state["powerbi_news_page"] = max(page_index - 1, 0)
            st.rerun()
    with page_col:
        st.markdown(
            f'<div class="folio-powerbi-page-indicator">{page_index + 1} / {total_pages}</div>',
            unsafe_allow_html=True,
        )
    with next_col:
        if st.button("→", key="powerbi_news_next", disabled=page_index >= total_pages - 1, use_container_width=True):
            st.session_state["powerbi_news_page"] = min(page_index + 1, total_pages - 1)
            st.rerun()


def _group_by(rows: Iterable[dict[str, str]], key: str) -> "OrderedDict[str, list[dict[str, str]]]":
    groups: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in rows:
        label = row.get(key) or "기타"
        groups.setdefault(label, []).append(row)
    return groups


def _build_news_items(
    update_rows: list[dict[str, str]],
    changelog_rows: list[dict[str, str]],
) -> list[PowerBINewsItem]:
    items: list[PowerBINewsItem] = []
    for release_label, rows in _group_by(update_rows, "release_label").items():
        overview = _find_overview(rows)
        version = _first_value(rows, "version")
        title = _localize_release_label(release_label)
        if version:
            title = f"{title} · v{version}"
        items.append(
            PowerBINewsItem(
                sort_date=_release_sort_date(release_label),
                label="월간 정기 업데이트",
                title=title,
                source_row=overview or _first(rows) or {},
                bullets=_release_summary_bullets(rows),
            )
        )

    for release_label, rows in _group_by(changelog_rows, "release_label").items():
        version = _first_value(rows, "version")
        released_at = _first_value(rows, "released_at")
        title_parts = [_localize_release_label(release_label)]
        if version:
            title_parts.append(f"v{version}")
        if released_at:
            title_parts.append(_localize_date(released_at))
        items.append(
            PowerBINewsItem(
                sort_date=_date_sort_value(released_at) or _release_sort_date(release_label),
                label="패치 로그",
                title=" · ".join(title_parts),
                source_row=_first(rows) or {},
                bullets=_changelog_summary_bullets(rows),
            )
        )

    return sorted(items, key=lambda item: item.sort_date, reverse=True)


def _find_overview(rows: list[dict[str, str]]) -> dict[str, str] | None:
    for row in rows:
        if (row.get("section") or "").lower() == "overview":
            return row
    return _first(rows)


def _first(rows: list[dict[str, str]]) -> dict[str, str] | None:
    return rows[0] if rows else None


def _first_value(rows: list[dict[str, str]], key: str) -> str:
    for row in rows:
        value = row.get(key)
        if value:
            return value
    return ""


def _source_link(row: dict[str, str], *, label: str = "원문 보기") -> str:
    source_url = row.get("source_url")
    if not source_url:
        return ""
    return f'<a class="folio-powerbi-link" href="{html.escape(source_url, quote=True)}" target="_blank" rel="noopener">{_escape(label)}</a>'


def _summary_bullets_html(items: list[str]) -> str:
    if not items:
        return ""
    bullets = "".join(f"<li>{_escape(item)}</li>" for item in items)
    return f'<ul class="folio-powerbi-summary-list">{bullets}</ul>'


def _release_summary_bullets(rows: list[dict[str, str]]) -> list[str]:
    bullets: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if (row.get("section") or "").lower() == "overview":
            continue
        bullet = _plain_update_bullet(row)
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
        bullet = _localize_fix(row.get("fix_en"))
        if not bullet or bullet in seen:
            continue
        seen.add(bullet)
        bullets.append(bullet)
        if len(bullets) >= 5:
            break
    return bullets


def _plain_update_bullet(row: dict[str, str]) -> str:
    raw_title = (
        row.get("feature_title_en")
        or row.get("feature_title_ko")
        or row.get("title_en")
        or row.get("title_ko")
        or ""
    )
    title = raw_title.lower()
    section = _localize_section(row.get("section"))

    if "dataviz world championship" in title:
        return "Power BI 커뮤니티 시각화 대회 일정이 공개되었습니다."
    if "fabcon" in title:
        return "Fabric 및 Power BI 컨퍼런스 등록과 세션 정보가 업데이트되었습니다."
    if "fabric apps" in title and "semantic" in title:
        return "의미 체계 모델을 기반으로 업무용 데이터 앱을 만드는 Fabric 앱 기능이 미리 보기로 추가되었습니다."
    if "copilot" in title and "web modeling" in title:
        return "웹 모델링 화면에서 Copilot이 모델 작성과 수정 작업을 보조합니다."
    if "report authoring agent" in title:
        return "AI가 보고서 작성 과정의 일부를 대신 수행하도록 에이전트 기능이 미리 보기로 추가되었습니다."
    if "data answering" in title and "m365" in title:
        return "Microsoft 365 Copilot Chat에서 데이터 질문에 답하는 기능이 실험적으로 제공됩니다."
    if "data answering" in title:
        return "Fabric Skills와 협업 도구에서 데이터 질문에 답하는 기능이 실험적으로 제공됩니다."
    if "explore improvements" in title:
        return "Copilot 기반 데이터 탐색 흐름이 개선되어 필요한 인사이트를 더 빠르게 찾을 수 있습니다."
    if "summary shortcut" in title:
        return "Copilot 요약을 바로 실행할 수 있는 단축 기능이 추가되었습니다."
    if "shape map" in title:
        return "Shape Map 시각적 개체가 정식 기능으로 전환되어 지도 기반 표현을 더 안정적으로 사용할 수 있습니다."
    if "date picker" in title or "slicer" in title:
        return "슬라이서에 날짜 선택 기능이 추가되어 기간 필터를 더 쉽게 설정할 수 있습니다."
    if "user-defined function" in title or "udf" in title:
        return "DAX 사용자 정의 함수가 확장되어 반복 계산 로직을 더 깔끔하게 관리할 수 있습니다."
    if "matrix" in title:
        return "행렬 시각적 개체의 표시와 상호작용 기능이 개선되었습니다."
    if "visual calculation" in title and "custom total" in title:
        return "시각적 계산과 사용자 지정 합계가 정식 제공되어 보고서 안에서 계산 결과를 더 유연하게 보여줄 수 있습니다."
    if "custom total" in title:
        return "사용자 지정 합계 옵션이 늘어나 합계 행을 보고서 의도에 맞게 조정할 수 있습니다."
    if "scatter" in title:
        return "분산형 차트에서 데이터 포인트를 더 잘 비교할 수 있도록 시각화 옵션이 개선되었습니다."
    if "bar" in title or "column" in title:
        return "막대 및 열 차트의 표현 옵션이 보강되었습니다."
    if "card" in title:
        return "카드 시각적 개체에서 핵심 지표를 보여주는 방식이 개선되었습니다."
    if "azure map" in title or "maps" in title:
        return "Azure 지도와 지도 시각화 관련 표시 옵션이 개선되었습니다."
    if "tooltip" in title:
        return "도구 설명에서 보조 정보를 보여주는 방식이 개선되었습니다."
    if "model" in title:
        return "데이터 모델링 작업을 더 쉽게 관리할 수 있는 기능이 추가되었습니다."
    if "connector" in title or "data connectivity" in title:
        return "외부 데이터 연결과 커넥터 관련 기능이 업데이트되었습니다."
    if "preview" in title:
        return f"{section} 영역에 새 미리 보기 기능이 추가되었습니다."
    if "general availability" in title or "generally available" in title:
        return f"{section} 영역의 미리 보기 기능이 정식 기능으로 전환되었습니다."

    localized_title = _localize_title(raw_title)
    return f"{section}: {localized_title}" if section and localized_title else localized_title


def _localize_release_label(value: str | None) -> str:
    text = str(value or "").strip()
    month_map = {
        "January": "1월",
        "February": "2월",
        "March": "3월",
        "April": "4월",
        "May": "5월",
        "June": "6월",
        "July": "7월",
        "August": "8월",
        "September": "9월",
        "October": "10월",
        "November": "11월",
        "December": "12월",
    }
    for english, korean in month_map.items():
        text = text.replace(english, korean)
    return text.replace("update", "업데이트")


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


def _localize_date(value: str | None) -> str:
    text = str(value or "").strip()
    month_map = {
        "January": "1월",
        "February": "2월",
        "March": "3월",
        "April": "4월",
        "May": "5월",
        "June": "6월",
        "July": "7월",
        "August": "8월",
        "September": "9월",
        "October": "10월",
        "November": "11월",
        "December": "12월",
    }
    for english, korean in month_map.items():
        text = text.replace(english, korean)
    return text


def _localize_section(value: str | None) -> str:
    section = str(value or "").strip()
    section_map = {
        "Overview": "요약",
        "General": "일반",
        "Copilot and AI": "Copilot 및 AI",
        "Reporting": "보고서",
        "Modeling": "모델링",
        "Data connectivity": "데이터 연결",
        "Visualizations": "시각화",
        "Other": "기타",
    }
    return section_map.get(section, _localize_title(section))


def _localize_title(value: str | None) -> str:
    text = str(value or "").strip()
    replacements = {
        "update": "업데이트",
        "announcement": "공지",
        "registration": "등록",
        "Preview": "미리 보기",
        "General Availability": "정식 제공",
        "Semantic Models": "의미 체계 모델",
        "semantic models": "의미 체계 모델",
        "modeling": "모델링",
        "visual": "시각적 개체",
        "visuals": "시각적 개체",
        "slicer": "슬라이서",
        "Slicer": "슬라이서",
        "Maps": "지도",
        "Azure Maps": "Azure 지도",
        "Matrix": "행렬",
        "Card": "카드",
        "Tooltip": "도구 설명",
        "tooltips": "도구 설명",
        "DAX": "DAX",
        "Fabric Apps": "Fabric 앱",
        "Copilot": "Copilot",
        "Power BI": "Power BI",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _localize_fix(value: str | None) -> str:
    original = str(value or "").strip().rstrip(".")
    if not original:
        return "변경 로그 항목"
    title = original.lower()

    if "data label positioning" in title and "column chart" in title:
        return "열 차트에서 데이터 레이블 위치가 어긋나던 문제가 수정되었습니다."
    if "native queries" in title and "export queries" in title:
        return "쿼리 내보내기에서 네이티브 쿼리를 출력 대상으로 저장할 때 실패하던 문제가 수정되었습니다."
    if "selected marker fill color" in title and "azure maps" in title:
        return "Azure 지도에서 선택한 마커 채우기 색상이 적용되지 않던 문제가 수정되었습니다."
    if "adbc driver assemblies" in title:
        return "ADBC 드라이버 어셈블리가 누락되던 문제가 수정되었습니다."
    if "view switcher icons" in title:
        return "Power BI Desktop에서 보기 전환 아이콘이 올바르게 표시되지 않던 문제가 수정되었습니다."
    if "empty schema" in title and "multimodel" in title:
        return "여러 모델을 함께 작성할 때 스키마가 비어 있는 것으로 처리되어 Copilot이나 모델 작성 화면에서 오류가 나던 문제가 수정되었습니다."
    if "calculated tables" in title and "refresh" in title:
        return "계산 테이블이 새로 고침 과정에서 누락되던 문제가 수정되었습니다."
    if "treat calculated tables as refreshable" in title:
        return "계산 테이블도 새로 고침 대상에 포함되도록 동작이 업데이트되었습니다."
    if "snowflake connector" in title and "directquery" in title:
        return "Snowflake 커넥터를 DirectQuery 모드로 사용할 때 지원되지 않는 쿼리 오류가 발생하던 문제가 수정되었습니다."
    if "pbip files" in title and "hangs" in title:
        return "연결 또는 파일 오류가 있는 PBIP 파일을 열 때 Power BI Desktop이 멈추던 문제가 수정되었습니다."
    if "oracle managed odp provider" in title:
        return "Oracle Managed ODP Provider 미리 보기 기능의 기본 설정이 일부 TNS alias 환경에서 실패하지 않도록 되돌려졌습니다."
    if "copilot orchestration throttling" in title:
        return "Copilot 오케스트레이션 제한 오류가 사용자 오류로 올바르게 분류되도록 수정되었습니다."
    if "refreshing tables" in title and "directquery" in title:
        return "DirectQuery 테이블을 새로 고침할 때 오류가 표시되던 문제가 수정되었습니다."
    if "unable to save" in title and "composite model" in title:
        return "LiveConnect에서 복합 모델로 변환한 뒤 보고서를 저장하지 못하던 문제가 수정되었습니다."
    if "queries" in title and "powerquery editor" in title:
        return "Power Query 편집기에서 쿼리 섹션이 보이지 않던 문제가 수정되었습니다."
    if "column or measure not found" in title:
        return "저장 시 '열 또는 측정값을 모델에서 찾을 수 없음' 오류가 발생하던 문제가 수정되었습니다."
    if "azure maps conversion dialog" in title:
        return "제한된 사용자에게 Azure Maps 변환 대화상자가 노출되던 문제가 수정되었습니다."
    if "ui buttons" in title and "conditional visibility" in title:
        return "조건부 표시 기능과 관련해 UI 버튼이 잘못 표시되던 문제가 수정되었습니다."
    if "databricks sql endpoint" in title:
        return "Databricks SQL Endpoint 연결 문제가 수정되었습니다."
    if "gen1 dataflows" in title:
        return "Gen1 Dataflows에서 향상된 컴퓨팅을 사용할 때 DirectQuery가 실패하던 문제가 수정되었습니다."
    if "pbir versioning" in title:
        return "Translytical task flows 미리 보기에서 PBIR 버전 관리 문제가 수정되었습니다."
    if "count-distinct" in title and "incorrect result" in title:
        return "Snowflake 쿼리의 count-distinct 계산이 잘못된 결과를 반환하던 문제가 수정되었습니다."
    if "creating relationships" in title and "snowflake" in title:
        return "Snowflake 연결 상태에서 관계를 만들 때 개체 참조 오류가 발생하던 문제가 수정되었습니다."
    if "ungrouping visuals" in title:
        return "시각적 개체 그룹을 해제한 뒤 페이지 이동이나 시각화 표시가 잘못되던 문제가 수정되었습니다."
    if "dataflow refresh" in title:
        return "Power BI Desktop에서 Dataflow 새로 고침이 실패하던 문제가 수정되었습니다."
    if "model.abf is stale" in title:
        return "로컬 model.abf가 오래된 상태일 때 모델을 열며 테이블 새로 고침이 실패하던 문제가 수정되었습니다."
    if "region not supported" in title:
        return "Copilot에서 알 수 없는 오류 코드가 발생할 때 더 이해하기 쉬운 '지역 미지원' 메시지로 표시되도록 수정되었습니다."
    if "index was outside the bounds" in title:
        return "커넥터 Implementation 2.0 사용 시 배열 범위 오류가 발생하던 문제가 수정되었습니다."
    if "incremental refresh validation" in title:
        return "여러 데이터 원본을 참조하는 테이블의 증분 새로 고침 검증 문제가 수정되었습니다."
    if "high-contrast mode" in title and "manage relationships" in title:
        return "고대비 모드에서 관계 관리 창의 체크박스와 아이콘이 왜곡되어 보이던 문제가 수정되었습니다."

    text = original
    replacements = {
        "Fixed an issue where ": "",
        "Fixed issues with ": "",
        "Fixed issue where ": "",
        "Addressed an issue of ": "",
        "Addressed an issue where ": "",
        "wasn't": "적용되지 않던 문제가",
        "failed": "실패하던 문제가",
        "missing": "누락되던 문제가",
        "data label positioning": "데이터 레이블 위치",
        "column charts": "열 차트",
        "native queries": "네이티브 쿼리",
        "Export queries": "쿼리 내보내기",
        "output destination": "출력 대상",
        "selected marker fill color": "선택한 마커 채우기 색상",
        "Azure Maps": "Azure 지도",
        "ADBC driver assemblies": "ADBC 드라이버 어셈블리",
        " in ": " 관련 ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    if not text.endswith(("수정", "개선", "해결")):
        text = f"{text} 수정"
    return text


def _escape(value: object) -> str:
    return html.escape(str(value or "").strip())
