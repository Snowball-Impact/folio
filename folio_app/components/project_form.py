import html

import streamlit as st

from folio_app.components.project_body import (
    parse_project_body,
    plain_project_body_text,
    render_project_body_editor,
)
from folio_app.components.ui import clean_html, plain_text, render_project_card_html
from folio_app.services.projects import normalize_optional_url, normalize_power_bi_embed_url


PROJECT_TITLE_MAX_CHARS = 48
PROJECT_ONE_LINER_MAX_CHARS = 56


def validate_project_form(form_data: dict[str, str]) -> tuple[dict[str, str], list[str], str | None]:
    parsed_body = parse_project_body(form_data["project_body"])
    missing = []
    if not form_data["title"].strip():
        missing.append("프로젝트명")
    if not _project_body_has_content(form_data["project_body"], parsed_body):
        missing.append("프로젝트 본문")

    text_errors = _validate_text_lengths(form_data)
    url_error = _validate_optional_urls(
        form_data["power_bi_url"],
        form_data["report_url"],
        form_data["github_url"],
        form_data["thumbnail_url"],
    )
    if text_errors:
        url_error = "\n".join([*text_errors, *([url_error] if url_error else [])])
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
    parsed_text = " ".join(plain_project_body_text(value) for value in parsed_body.values())
    raw_text = plain_project_body_text(body)
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
    _render_project_form_intro()

    with st.container(border=True, key=f"{key_prefix}_form_section_overview"):
        overview_col, preview_col = st.columns([3, 2], gap="large")
        with overview_col:
            _render_form_section_heading("기본 정보", "프로젝트를 한눈에 이해할 수 있는 정보를 입력하세요.")
            title_input = st.text_input(
                "프로젝트명 *",
                value=title,
                placeholder="예: 서울시 청년 취업 데이터 분석",
                help=f"홈 갤러리 카드 제목 영역에 맞춰 최대 {PROJECT_TITLE_MAX_CHARS}자까지 입력할 수 있습니다.",
                max_chars=PROJECT_TITLE_MAX_CHARS,
                key=f"{key_prefix}_title",
            )
            one_liner_input = st.text_input(
                "프로젝트 한 줄 소개",
                value=one_liner,
                placeholder="핵심 메시지를 한 문장으로 적어주세요.",
                help=f"홈 갤러리 카드 요약 영역에 맞춰 최대 {PROJECT_ONE_LINER_MAX_CHARS}자까지 입력할 수 있습니다.",
                max_chars=PROJECT_ONE_LINER_MAX_CHARS,
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

        with preview_col:
            st.markdown(
                '<div class="folio-form-preview-heading"><strong>카드 미리보기</strong></div>',
                unsafe_allow_html=True,
            )
            _render_project_preview(title_input, one_liner_input, tags_input, "")

    with st.container(border=True, key=f"{key_prefix}_form_section_content"):
        _render_form_section_heading("프로젝트 내용", "분석의 배경과 과정, 핵심 인사이트를 기록하세요.")
        project_body = render_project_body_editor(f"{key_prefix}_body", project_body_initial)

    with st.container(border=True, key=f"{key_prefix}_form_section_links"):
        _render_form_section_heading("관련 결과물 링크", "관련 결과물을 연결할 수 있습니다. 선택 입력 항목입니다.")
        power_bi_col, github_col, etc_col = st.columns(3, gap="medium")
        with power_bi_col:
            power_bi_url_input = st.text_input(
                "BI Platform Embed URL",
                value=power_bi_url,
                placeholder="https://... 또는 iframe 코드",
                help="BI Platform 에서 복사한 iframe 코드 전체를 붙여넣어도 됩니다. 저장 시 src URL만 추출합니다.",
                key=f"{key_prefix}_power_bi_url",
            )
            _render_url_feedback(power_bi_url_input, "BI Platform Embed URL", power_bi=True)
        with github_col:
            github_url_input = st.text_input(
                "GitHub URL",
                value=github_url,
                placeholder="https://github.com/...",
                key=f"{key_prefix}_github_url",
            )
            _render_url_feedback(github_url_input, "GitHub URL")
        with etc_col:
            etc_url_input = st.text_input(
                "ETC URL",
                value=etc_url,
                placeholder="https://...",
                key=f"{key_prefix}_etc_url",
            )
            _render_url_feedback(etc_url_input, "ETC URL")

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


def _render_project_form_intro() -> None:
    st.markdown(
        """
        <div class="folio-project-form-intro">
            <strong>프로젝트 정보를 작성해 주세요.</strong>
            <span>작성 내용은 현재 세션에 자동 임시 저장됩니다.</span>
            <small><b>*</b> 필수 입력</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_form_section_heading(title: str, body: str) -> None:
    st.markdown(
        clean_html(f"""
        <div class="folio-form-section-heading">
            <div>
                <strong>{html.escape(title)}</strong>
                <small>{html.escape(body)}</small>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
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


def _validate_text_lengths(form_data: dict[str, str]) -> list[str]:
    errors = []
    if len(form_data.get("title", "")) > PROJECT_TITLE_MAX_CHARS:
        errors.append(f"프로젝트명은 최대 {PROJECT_TITLE_MAX_CHARS}자까지 입력할 수 있습니다.")
    if len(form_data.get("one_liner", "")) > PROJECT_ONE_LINER_MAX_CHARS:
        errors.append(f"프로젝트 한 줄 소개는 최대 {PROJECT_ONE_LINER_MAX_CHARS}자까지 입력할 수 있습니다.")
    return errors


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
