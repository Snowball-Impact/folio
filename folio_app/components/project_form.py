import html
import re

import streamlit as st

from folio_app.components.ui import plain_text, render_project_card_html
from folio_app.services.project_content import sanitize_project_html
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
        value=_html_to_markdownish(value),
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

    if not any(_strip_html(value).strip() for value in sections.values()):
        sections["problem"] = _clean_rich_text_section(body)

    return sections


def _clean_rich_text_section(value: str) -> str:
    cleaned = value.strip()
    if cleaned in {"", "<p><br></p>", "<p></p>"}:
        return ""
    return cleaned


def _plain_body_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    for heading in ["문제 정의", "사용 데이터", "분석 과정", "핵심 인사이트"]:
        text = text.replace(heading, " ")
    return " ".join(html.unescape(text).split())


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
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value or "")).split())


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
    if not _project_body_has_content(form_data["project_body"], parsed_body):
        missing.append("프로젝트 본문")

    url_error = _validate_optional_urls(
        form_data["power_bi_url"],
        form_data["report_url"],
        form_data["github_url"],
        form_data["thumbnail_url"],
    )
    return parsed_body, missing, url_error


def build_project_payload(form_data: dict[str, str], parsed_body: dict[str, str]) -> dict:
    return {
        "title": form_data["title"],
        "one_liner": form_data["one_liner"],
        "problem": parsed_body["problem"],
        "dataset": parsed_body["dataset"],
        "process": parsed_body["process"],
        "insights": parsed_body["insights"],
        "power_bi_url": form_data["power_bi_url"],
        "report_url": form_data["report_url"],
        "github_url": form_data["github_url"],
        "thumbnail_url": form_data["thumbnail_url"],
        "tags": form_data["tags"],
        "is_public": form_data["is_public"],
    }


def _project_body_has_content(body: str, parsed_body: dict[str, str]) -> bool:
    parsed_text = " ".join(_plain_body_text(value) for value in parsed_body.values())
    raw_text = _plain_body_text(body)
    return bool(parsed_text.strip() or raw_text.strip())


def render_project_form(
    key_prefix: str,
    title: str,
    one_liner: str,
    tags: str,
    project_body_initial: str,
    power_bi_url: str,
    github_url: str,
    etc_url: str,
    submit_label: str,
    thumbnail_url: str = "",
    is_public: bool = True,
    show_visibility_setting: bool = False,
    secondary_label: str | None = None,
) -> tuple[dict[str, str], bool, bool]:
    st.markdown(
        """
        <div class="folio-project-form-intro">
            <strong>프로젝트 정보를 작성해 주세요.</strong>
            <span><b>*</b> 표시는 필수 입력 항목입니다.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("작성 중에는 페이지를 새로고침하지 마세요. 등록 또는 수정이 완료되기 전까지 내용은 현재 세션에만 유지됩니다.")

    overview_col, links_col = st.columns(2, gap="large")
    with overview_col:
        with st.container(border=True, key=f"{key_prefix}_form_section_overview"):
            st.markdown(
                '<div class="folio-form-section-heading"><span>1</span><div><strong>기본 정보</strong><small>프로젝트를 한눈에 이해할 수 있는 정보를 입력하세요.</small></div></div>',
                unsafe_allow_html=True,
            )
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
                help="#은 자동으로 제거되고 쉼표 기준으로 최대 10개까지 저장됩니다.",
                key=f"{key_prefix}_tags",
            )
            preview_tags = _normalize_tag_preview(tags_input)
            if preview_tags:
                tag_preview = " ".join(f"`#{tag}`" for tag in preview_tags)
                st.caption(f"저장될 태그: {tag_preview}")
            if _raw_tag_count(tags_input) > 10:
                st.warning("태그는 앞에서부터 최대 10개까지만 저장됩니다.")

    with links_col:
        with st.container(border=True, key=f"{key_prefix}_form_section_links"):
            st.markdown(
                '<div class="folio-form-section-heading"><span>3</span><div><strong>관련 결과물 링크</strong><small>관련 결과물을 연결할 수 있습니다. 선택 입력 항목입니다.</small></div></div>',
                unsafe_allow_html=True,
            )
            power_bi_url_input = st.text_input(
                "BI Platform Embed URL",
                value=power_bi_url,
                help="BI Platform 에서 복사한 iframe 코드 전체를 붙여넣어도 됩니다. 저장 시 src URL만 추출합니다.",
                key=f"{key_prefix}_power_bi_url",
            )
            _render_url_feedback(power_bi_url_input, "BI Platform Embed URL", power_bi=True)

            github_url_input = st.text_input(
                "GitHub URL",
                value=github_url,
                key=f"{key_prefix}_github_url",
            )
            _render_url_feedback(github_url_input, "GitHub URL")

            etc_url_input = st.text_input(
                "ETC URL",
                value=etc_url,
                key=f"{key_prefix}_etc_url",
            )
            _render_url_feedback(etc_url_input, "ETC URL")

    with st.container(border=True, key=f"{key_prefix}_form_section_content"):
        st.markdown(
            '<div class="folio-form-section-heading"><span>2</span><div><strong>프로젝트 내용</strong><small>분석의 배경과 과정, 핵심 인사이트를 기록하세요.</small></div></div>',
            unsafe_allow_html=True,
        )
        project_body = render_project_body_editor(f"{key_prefix}_body", project_body_initial)

    if st.toggle("등록 전 카드 미리보기", key=f"{key_prefix}_preview"):
        _render_project_preview(
            title_input,
            one_liner_input,
            tags_input,
            project_body,
        )

    cancelled = False
    if show_visibility_setting:
        visibility_col, actions_col = st.columns([2, 1], gap="large", vertical_alignment="bottom")
        with visibility_col, st.container(border=True, key=f"{key_prefix}_visibility_setting"):
            st.markdown(
                '<div class="folio-visibility-setting-copy"><strong>공개 설정</strong><span>공개를 끄면 목록과 검색에서 숨겨지고 작성자만 볼 수 있습니다.</span></div>',
                unsafe_allow_html=True,
            )
            is_public_input = st.toggle(
                "프로젝트 공개",
                value=is_public,
                key=f"{key_prefix}_is_public",
            )
        with actions_col:
            secondary_col, action_col = st.columns(2)
            with secondary_col:
                cancelled = st.button(
                    secondary_label or "목록으로 돌아가기",
                    use_container_width=True,
                    key=f"{key_prefix}_secondary",
                )
            with action_col:
                submitted = st.button(
                    submit_label,
                    type="primary",
                    use_container_width=True,
                    key=f"{key_prefix}_submit",
                )
    elif secondary_label:
        is_public_input = is_public
        action_space, secondary_col, action_col = st.columns([2, 1, 1])
        with secondary_col:
            cancelled = st.button(
                secondary_label,
                use_container_width=True,
                key=f"{key_prefix}_secondary",
            )
        with action_col:
            submitted = st.button(
                submit_label,
                type="primary",
                use_container_width=True,
                key=f"{key_prefix}_submit",
            )
    else:
        is_public_input = is_public
        action_space, action_col = st.columns([3, 1])
        with action_col:
            submitted = st.button(
                submit_label,
                type="primary",
                use_container_width=True,
                key=f"{key_prefix}_submit",
            )
    return (
        {
            "title": title_input,
            "one_liner": one_liner_input,
            "tags": tags_input,
            "project_body": project_body,
            "power_bi_url": power_bi_url_input,
            # ETC URL is stored in the legacy report_url column. Thumbnail is
            # no longer editable, but retaining it prevents edits from clearing it.
            "report_url": etc_url_input,
            "github_url": github_url_input,
            "thumbnail_url": thumbnail_url,
            "is_public": is_public_input,
        },
        submitted,
        cancelled,
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


def _normalize_tag_preview(value: str) -> list[str]:
    tags = []
    for tag in value.replace("#", "").split(","):
        normalized = tag.strip()
        if normalized and normalized not in tags:
            tags.append(normalized)
    return tags[:10]


def _raw_tag_count(value: str) -> int:
    return len({tag.strip() for tag in value.replace("#", "").split(",") if tag.strip()})


def _render_url_feedback(value: str, label: str, *, power_bi: bool = False) -> None:
    if not value.strip():
        return
    normalized = normalize_power_bi_embed_url(value) if power_bi else normalize_optional_url(value)
    if normalized is None:
        guidance = "iframe 코드 또는 http(s) 주소가 필요합니다." if power_bi else "http:// 또는 https:// 주소가 필요합니다."
        st.error(f"{label} 형식을 확인하세요. {guidance}")


def _render_project_preview(
    title: str,
    one_liner: str,
    tags: str,
    project_body: str,
) -> None:
    preview = {
        "title": title.strip() or "프로젝트명이 여기에 표시됩니다.",
        "one_liner": one_liner.strip(),
        "insights": plain_text(project_body),
        "tags": _normalize_tag_preview(tags),
        "view_count": 0,
        "like_count": 0,
    }
    st.markdown(
        render_project_card_html(preview, fallback_text="프로젝트 소개가 여기에 표시됩니다."),
        unsafe_allow_html=True,
    )
