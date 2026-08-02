"""Project body editor, template, and section parsing."""

from __future__ import annotations

import html
import re

import streamlit as st

from folio_app.services.project_content import sanitize_project_html


def _get_quill_editor():
    try:
        from streamlit_quill import st_quill

        return st_quill
    except ImportError:
        return None


PROJECT_BODY_TEMPLATE = """<h2>문제 정의</h2>
<p>이 프로젝트는 [대상/상황]에서 발생하는 [문제]를 다룹니다. 이를 분석한 이유는 [의사결정/개선 목표]를 더 명확히 하기 위해서입니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 이 프로젝트는 청년 구직자가 교육 수료 후 취업까지 이어지는 과정에서 발생하는 이탈 문제를 다룹니다. 이를 분석한 이유는 어떤 요인이 취업 성과에 영향을 주는지 확인하기 위해서입니다.</span></p>
<h2>사용 데이터</h2>
<p>사용한 데이터는 [출처]의 [기간/범위] 데이터입니다. 주요 변수는 [변수1], [변수2], [변수3]이며, 핵심 지표는 [지표]입니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 사용한 데이터는 교육 운영 시스템의 2025년 수강생 데이터입니다. 주요 변수는 수강 과정, 출석률, 과제 제출 여부이며, 핵심 지표는 수료율과 취업 연계율입니다.</span></p>
<h2>분석 과정</h2>
<p>먼저 [기준]으로 데이터를 나누어 비교했습니다. 이후 [분석 방법]을 통해 [패턴/차이]를 확인하고, [판단 기준]을 중심으로 결과를 해석했습니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 먼저 과정별로 수료율과 취업 연계율을 비교했습니다. 이후 출석률 구간에 따라 성과 차이를 확인하고, 수료 여부와 취업 여부의 관계를 중심으로 결과를 해석했습니다.</span></p>
<h2>핵심 인사이트</h2>
<p>분석 결과 [핵심 발견]을 확인했습니다. 따라서 [대상/조직]은 [추천 행동]을 우선 검토할 필요가 있습니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 분석 결과 출석률이 높은 수강생일수록 수료와 취업 연계 가능성이 함께 높아지는 경향을 확인했습니다. 따라서 교육 운영팀은 중도 이탈 위험이 높은 수강생을 조기에 발견하고 개입하는 방안을 우선 검토할 필요가 있습니다.</span></p>
"""


def render_project_body_editor(key: str, value: str) -> str:
    st.caption("자유롭게 작성하세요. 섹션 제목을 유지하면 상세 화면에서 내용이 더 깔끔하게 나뉩니다.")
    st_quill = _get_quill_editor()
    if st_quill is not None:
        body = st_quill(
            value=value,
            html=True,
            placeholder="프로젝트의 문제 정의, 사용 데이터, 분석 과정, 핵심 인사이트를 작성하세요.",
            key=key,
        )
        with st.expander("본문 미리보기"):
            st.markdown(
                sanitize_project_html(body) or "_입력한 본문이 여기에 표시됩니다._",
                unsafe_allow_html=True,
            )
        return body or ""

    st.warning("서식 편집기를 사용하려면 `pip install -r requirements.txt`를 실행하세요.")
    body = st.text_area(
        "프로젝트 본문 *",
        value=html_to_markdownish(value),
        height=420,
        key=key,
        help="Markdown 서식을 사용할 수 있습니다. 섹션 제목은 선택 사항입니다.",
    )
    with st.expander("본문 미리보기"):
        st.markdown(body or "_입력한 본문이 여기에 표시됩니다._")
    return body


def parse_project_body(body: str) -> dict[str, str]:
    if "<h2" in body.lower():
        return _parse_project_body_html(body)

    sections = {
        "problem": "",
        "dataset": "",
        "process": "",
        "insights": "",
    }
    title_map = {
        "문제 정의": "problem",
        "사용 데이터": "dataset",
        "분석 과정": "process",
        "핵심 인사이트": "insights",
    }
    current_key: str | None = None
    collected: dict[str, list[str]] = {key: [] for key in sections}

    for line in body.splitlines():
        heading = line.strip().lstrip("#").strip()
        if line.strip().startswith("#") and heading in title_map:
            current_key = title_map[heading]
            continue
        if current_key:
            collected[current_key].append(line)

    for key, lines in collected.items():
        sections[key] = "\n".join(lines).strip()

    if not any(sections.values()):
        sections["problem"] = body.strip()

    return sections


def project_body_from_project(project: dict) -> str:
    return "".join(
        [
            f"<h2>문제 정의</h2>{format_body_value(project.get('problem'))}",
            f"<h2>사용 데이터</h2>{format_body_value(project.get('dataset'))}",
            f"<h2>분석 과정</h2>{format_body_value(project.get('process'))}",
            f"<h2>핵심 인사이트</h2>{format_body_value(project.get('insights'))}",
        ]
    )


def plain_project_body_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    for heading in ["문제 정의", "사용 데이터", "분석 과정", "핵심 인사이트"]:
        text = text.replace(heading, " ")
    return " ".join(html.unescape(text).split())


def format_body_value(value: str | None) -> str:
    if not value:
        return "<p></p>"
    if "<" in value and ">" in value:
        return value
    paragraphs = [line.strip() for line in value.splitlines() if line.strip()]
    if not paragraphs:
        return "<p></p>"
    return "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs)


def strip_html(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value or "")).split())


def html_to_markdownish(value: str) -> str:
    return (
        value.replace("<h2>", "## ")
        .replace("</h2>", "\n\n")
        .replace("<p>", "")
        .replace("</p>", "\n\n")
        .replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
    )


def _parse_project_body_html(body: str) -> dict[str, str]:
    sections = {
        "problem": "",
        "dataset": "",
        "process": "",
        "insights": "",
    }
    title_map = {
        "문제 정의": "problem",
        "사용 데이터": "dataset",
        "분석 과정": "process",
        "핵심 인사이트": "insights",
    }

    parts = body.replace("\r\n", "\n")
    titles = "|".join(re.escape(title) for title in title_map)
    heading_pattern = re.compile(
        rf"<h2(?:\s[^>]*)?>\s*({titles})\s*</h2>",
        flags=re.IGNORECASE,
    )
    matches = list(heading_pattern.finditer(parts))
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        key = title_map.get(title)
        if key is None:
            continue
        section_end = matches[index + 1].start() if index + 1 < len(matches) else len(parts)
        sections[key] = _clean_rich_text_section(parts[match.end() : section_end])

    if not any(strip_html(value).strip() for value in sections.values()):
        sections["problem"] = _clean_rich_text_section(body)

    return sections


def _clean_rich_text_section(value: str) -> str:
    cleaned = value.strip()
    if cleaned in {"", "<p><br></p>", "<p></p>"}:
        return ""
    return cleaned
