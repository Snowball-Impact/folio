import html

import streamlit as st

from folio_app.services.projects import normalize_optional_url, normalize_power_bi_embed_url


def _get_quill_editor():
    try:
        from streamlit_quill import st_quill

        return st_quill
    except ImportError:
        return None


PROJECT_BODY_TEMPLATE = """<h2>문제 정의</h2>
<p></p>
<h2>사용 데이터</h2>
<p></p>
<h2>분석 과정</h2>
<p></p>
<h2>핵심 인사이트</h2>
<p></p>
"""


def render_project_body_editor(key: str, value: str) -> str:
    st.caption("본문의 네 섹션 제목은 유지하면 프로젝트 상세 화면에 깔끔하게 나뉘어 표시됩니다.")
    st_quill = _get_quill_editor()
    if st_quill is not None:
        body = st_quill(
            value=value,
            html=True,
            placeholder="프로젝트의 문제 정의, 사용 데이터, 분석 과정, 핵심 인사이트를 작성하세요.",
            key=key,
        )
        with st.expander("본문 미리보기"):
            st.markdown(body or "_입력한 본문이 여기에 표시됩니다._", unsafe_allow_html=True)
        return body or ""

    st.warning("서식 편집기를 사용하려면 `pip install -r requirements.txt`를 실행하세요.")
    body = st.text_area(
        "프로젝트 본문 *",
        value=_html_to_markdownish(value),
        height=420,
        key=key,
        help="Markdown 서식을 사용할 수 있습니다. ## 문제 정의, ## 핵심 인사이트 섹션은 필수입니다.",
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
            f"<h2>문제 정의</h2>{_format_body_value(project.get('problem'))}",
            f"<h2>사용 데이터</h2>{_format_body_value(project.get('dataset'))}",
            f"<h2>분석 과정</h2>{_format_body_value(project.get('process'))}",
            f"<h2>핵심 인사이트</h2>{_format_body_value(project.get('insights'))}",
        ]
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
    for title, key in title_map.items():
        marker = f"<h2>{title}</h2>"
        if marker not in parts:
            continue
        after_marker = parts.split(marker, 1)[1]
        next_positions = [
            after_marker.find(f"<h2>{next_title}</h2>")
            for next_title in title_map
            if next_title != title and after_marker.find(f"<h2>{next_title}</h2>") >= 0
        ]
        section_html = after_marker[: min(next_positions)] if next_positions else after_marker
        sections[key] = _clean_rich_text_section(section_html)

    if not any(_strip_html(value).strip() for value in sections.values()):
        sections["problem"] = _clean_rich_text_section(body)

    return sections


def _clean_rich_text_section(value: str) -> str:
    cleaned = value.strip()
    if cleaned in {"", "<p><br></p>", "<p></p>"}:
        return ""
    return cleaned


def _format_body_value(value: str | None) -> str:
    if not value:
        return "<p></p>"
    if "<" in value and ">" in value:
        return value
    paragraphs = [line.strip() for line in value.splitlines() if line.strip()]
    if not paragraphs:
        return "<p></p>"
    return "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs)


def _strip_html(value: str) -> str:
    text = value
    for token in ["<p>", "</p>", "<br>", "<br/>", "<br />", "<strong>", "</strong>", "<em>", "</em>"]:
        text = text.replace(token, " ")
    return html.unescape(text)


def _html_to_markdownish(value: str) -> str:
    return (
        value.replace("<h2>", "## ")
        .replace("</h2>", "\n\n")
        .replace("<p>", "")
        .replace("</p>", "\n\n")
        .replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
    )


def validate_project_form(form_data: dict[str, str]) -> tuple[dict[str, str], list[str], str | None]:
    parsed_body = parse_project_body(form_data["project_body"])
    missing = []
    if not form_data["title"].strip():
        missing.append("프로젝트명")
    if not parsed_body["problem"].strip():
        missing.append("문제 정의")
    if not parsed_body["insights"].strip():
        missing.append("핵심 인사이트")

    url_error = _validate_optional_urls(
        form_data["power_bi_url"],
        form_data["report_url"],
        form_data["github_url"],
        form_data["thumbnail_url"],
    )
    return parsed_body, missing, url_error


def build_project_payload(form_data: dict[str, str], parsed_body: dict[str, str], category: str) -> dict:
    return {
        "title": form_data["title"],
        "category": category,
        "one_liner": form_data["one_liner"],
        "problem": parsed_body["problem"],
        "dataset": parsed_body["dataset"],
        "process": parsed_body["process"],
        "insights": parsed_body["insights"],
        "power_bi_url": form_data["power_bi_url"],
        "report_url": form_data["report_url"],
        "github_url": form_data["github_url"],
        "thumbnail_url": form_data["thumbnail_url"],
        "ai_summary": form_data["ai_summary"],
        "tags": form_data["tags"],
    }


def render_project_form(
    key_prefix: str,
    title: str,
    one_liner: str,
    tags: str,
    project_body_initial: str,
    power_bi_url: str,
    report_url: str,
    github_url: str,
    thumbnail_url: str,
    ai_summary: str,
    submit_label: str,
) -> tuple[dict[str, str], bool]:
    st.markdown("### 프로젝트 정보")
    left, right = st.columns([2, 1])
    with left:
        title_input = st.text_input(
            "프로젝트명 *",
            value=title,
            placeholder="예: 서울시 청년 취업 데이터 분석",
            key=f"{key_prefix}_title",
        )
        one_liner_input = st.text_input(
            "프로젝트 한 줄 소개",
            value=one_liner,
            placeholder="핵심 메시지를 한 문장으로 적어주세요.",
            key=f"{key_prefix}_one_liner",
        )
        tags_input = st.text_input(
            "태그",
            value=tags,
            placeholder="공공데이터, PowerBI, 취업",
            key=f"{key_prefix}_tags",
        )
        project_body = render_project_body_editor(f"{key_prefix}_body", project_body_initial)

    with right:
        st.markdown("### 링크 및 요약")
        power_bi_url_input = st.text_input(
            "Power BI Embed URL",
            value=power_bi_url,
            help="Power BI에서 복사한 iframe 코드 전체를 붙여넣어도 됩니다. 저장 시 src URL만 추출합니다.",
            key=f"{key_prefix}_power_bi_url",
        )
        report_url_input = st.text_input(
            "보고서 URL",
            value=report_url,
            key=f"{key_prefix}_report_url",
        )
        github_url_input = st.text_input(
            "GitHub URL",
            value=github_url,
            key=f"{key_prefix}_github_url",
        )
        thumbnail_url_input = st.text_input(
            "썸네일 URL",
            value=thumbnail_url,
            key=f"{key_prefix}_thumbnail_url",
        )
        ai_summary_input = st.text_area(
            "AI 요약",
            value=ai_summary,
            height=110,
            key=f"{key_prefix}_ai_summary",
        )

    submitted = st.button(submit_label, use_container_width=True, key=f"{key_prefix}_submit")
    return (
        {
            "title": title_input,
            "one_liner": one_liner_input,
            "tags": tags_input,
            "project_body": project_body,
            "power_bi_url": power_bi_url_input,
            "report_url": report_url_input,
            "github_url": github_url_input,
            "thumbnail_url": thumbnail_url_input,
            "ai_summary": ai_summary_input,
        },
        submitted,
    )


def _validate_optional_urls(
    power_bi_url: str,
    report_url: str,
    github_url: str,
    thumbnail_url: str,
) -> str | None:
    if power_bi_url.strip() and normalize_power_bi_embed_url(power_bi_url) is None:
        return "Power BI Embed URL을 확인하세요. iframe 코드 또는 https URL을 입력해야 합니다."

    invalid_fields = []
    if report_url.strip() and normalize_optional_url(report_url) is None:
        invalid_fields.append("보고서 URL")
    if github_url.strip() and normalize_optional_url(github_url) is None:
        invalid_fields.append("GitHub URL")
    if thumbnail_url.strip() and normalize_optional_url(thumbnail_url) is None:
        invalid_fields.append("썸네일 URL")

    if invalid_fields:
        return f"{', '.join(invalid_fields)}은 http:// 또는 https://로 시작해야 합니다."
    return None
