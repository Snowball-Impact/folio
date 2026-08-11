import html
from typing import Any

import streamlit as st

from folio_app.config import get_settings
from folio_app.components.project_body import (
    parse_project_body,
    plain_project_body_text,
    render_project_body_editor,
)
from folio_app.components.ui import clean_html, plain_text, render_project_card_html
from folio_app.services.project_normalizers import (
    THUMBNAIL_MODE_AUTO_COVER,
    THUMBNAIL_MODE_CAPTURE,
    THUMBNAIL_MODE_MANUAL_URL,
)
from folio_app.services.projects import normalize_optional_url, normalize_power_bi_embed_url
from folio_app.services.project_references import REFERENCE_PLATFORM_BY_KEY, REFERENCE_PLATFORMS


PROJECT_TITLE_MAX_CHARS = 48
PROJECT_ONE_LINER_MAX_CHARS = 56
PROJECT_PLATFORM_OTHER_KEY = "other"
PROJECT_THUMBNAIL_MODE_OPTIONS = (
    THUMBNAIL_MODE_AUTO_COVER,
    THUMBNAIL_MODE_MANUAL_URL,
    THUMBNAIL_MODE_CAPTURE,
)


def validate_project_form(form_data: dict[str, Any]) -> tuple[dict[str, str], list[str], str | None]:
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
        form_data.get("thumbnail_mode", THUMBNAIL_MODE_AUTO_COVER),
        has_pbix_upload=form_data.get("pbix_file") is not None,
    )
    pbix_error = _validate_pbix_file(form_data)
    if text_errors:
        url_error = "\n".join([*text_errors, *([url_error] if url_error else [])])
    if pbix_error:
        url_error = "\n".join([*([url_error] if url_error else []), pbix_error])
    return parsed_body, missing, url_error


def build_project_payload(form_data: dict[str, Any], parsed_body: dict[str, str]) -> dict:
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
        "thumbnail_mode": form_data.get("thumbnail_mode", THUMBNAIL_MODE_AUTO_COVER),
        "project_type": project_type_for_platform(form_data.get("platform", PROJECT_PLATFORM_OTHER_KEY)),
        "embed_status": "supported" if form_data["power_bi_url"] else "external_only",
        "tags": tags_with_platform(form_data["tags"], form_data.get("platform", PROJECT_PLATFORM_OTHER_KEY)),
        "is_public": form_data["is_public"],
    }


def hero_preview_project(form_data: dict[str, Any], key_prefix: str) -> dict:
    title = str(st.session_state.get(f"{key_prefix}_title", form_data.get("title") or "") or "")
    one_liner = str(st.session_state.get(f"{key_prefix}_one_liner", form_data.get("one_liner") or "") or "")
    tags = str(st.session_state.get(f"{key_prefix}_tags", form_data.get("tags") or "") or "")
    platform = str(st.session_state.get(f"{key_prefix}_platform", form_data.get("platform") or PROJECT_PLATFORM_OTHER_KEY) or "")
    thumbnail_mode = str(
        st.session_state.get(f"{key_prefix}_thumbnail_mode", form_data.get("thumbnail_mode") or THUMBNAIL_MODE_AUTO_COVER)
        or THUMBNAIL_MODE_AUTO_COVER
    )
    thumbnail_url = ""
    if thumbnail_mode == THUMBNAIL_MODE_MANUAL_URL:
        thumbnail_url = str(st.session_state.get(f"{key_prefix}_thumbnail_url", form_data.get("thumbnail_url") or "") or "")
    return {
        "id": "submit-preview",
        "title": title.strip() or "프로젝트명이 여기에 표시됩니다.",
        "one_liner": one_liner.strip() or "프로젝트 한 줄 소개가 표시됩니다.",
        "tags": tags_with_platform(tags, platform),
        "thumbnail_url": thumbnail_url,
        "view_count": 0,
        "like_count": 0,
        "comment_count": 0,
    }


def tags_with_platform(tags: str, platform_key: str) -> list[str]:
    normalized_tags = _normalize_tag_preview(tags)
    platform_labels = {_normalized_tag(label) for _, label in _project_platform_options()}
    platform_labels.update(_normalized_tag(platform.label) for platform in REFERENCE_PLATFORMS)
    platform_labels.update(_normalized_tag(alias) for platform in REFERENCE_PLATFORMS for alias in platform.aliases)

    cleaned_tags = [tag for tag in normalized_tags if _normalized_tag(tag) not in platform_labels]
    if platform_key == PROJECT_PLATFORM_OTHER_KEY:
        return cleaned_tags[:10]

    platform = REFERENCE_PLATFORM_BY_KEY.get(platform_key)
    if not platform:
        return cleaned_tags[:10]
    return [platform.label, *cleaned_tags][:10]


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
    platform_key: str = PROJECT_PLATFORM_OTHER_KEY,
    thumbnail_url: str = "",
    thumbnail_mode: str = THUMBNAIL_MODE_AUTO_COVER,
    is_public: bool = True,
    show_visibility_setting: bool = False,
    allow_pbix_upload: bool = False,
    secondary_label: str | None = None,
) -> tuple[dict[str, Any], bool, bool]:
    _render_project_form_intro()

    with st.container(border=True, key=f"{key_prefix}_form_section_overview"):
        overview_col, resource_col = st.columns([1, 1], gap="large")
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
                placeholder="공공데이터, 시각화, 취업",
                help="#은 자동으로 제거되고 쉼표 기준으로 최대 10개까지 저장됩니다.",
                key=f"{key_prefix}_tags",
            )
            platform_input = _render_platform_selector(key_prefix, platform_key)
            preview_tags = tags_with_platform(tags_input, platform_input)
            if preview_tags:
                tag_preview = " ".join(f"`#{tag}`" for tag in preview_tags)
                st.caption(f"저장될 태그: {tag_preview}")
            if _raw_tag_count(tags_input) > 10:
                st.warning("태그는 앞에서부터 최대 10개까지만 저장됩니다.")

            thumbnail_mode_input = _current_thumbnail_mode(key_prefix, thumbnail_mode)
            thumbnail_url_input = _current_thumbnail_url(key_prefix, thumbnail_url, thumbnail_mode_input)

        with resource_col:
            _render_form_section_heading("산출물 링크", "공개 프로젝트에서 연결할 외부 산출물을 입력하세요.")
            power_bi_url_input = st.text_input(
                "Embed Code",
                value=power_bi_url,
                placeholder="https://... 또는 iframe 코드",
                help="BI Platform 에서 복사한 iframe 코드 전체를 붙여넣어도 됩니다. 저장 시 src URL만 추출합니다.",
                key=f"{key_prefix}_power_bi_url",
            )
            _render_url_feedback(power_bi_url_input, "Embed Code", power_bi=True)

            github_url_input = st.text_input(
                "GitHub URL",
                value=github_url,
                placeholder="https://github.com/...",
                key=f"{key_prefix}_github_url",
            )
            _render_url_feedback(github_url_input, "GitHub URL")

            etc_url_input = st.text_input(
                "Web Application URL",
                value=etc_url,
                placeholder="https://...",
                key=f"{key_prefix}_etc_url",
            )
            _render_url_feedback(etc_url_input, "Web Application URL")

            thumbnail_mode_input = _render_thumbnail_mode_selector(key_prefix, thumbnail_mode)
            thumbnail_url_input = ""
            if thumbnail_mode_input == THUMBNAIL_MODE_MANUAL_URL:
                thumbnail_url_input = st.text_input(
                    "썸네일 URL",
                    value=thumbnail_url,
                    placeholder="https://...",
                    key=f"{key_prefix}_thumbnail_url",
                )
                _render_url_feedback(thumbnail_url_input, "썸네일 URL")
            elif thumbnail_mode_input == THUMBNAIL_MODE_CAPTURE:
                thumbnail_url_input = thumbnail_url
                st.caption("등록 후 Embed Code 또는 Web Application URL 기준으로 대표 이미지를 생성합니다.")

    pbix_file = None
    if allow_pbix_upload and platform_input == "powerbi":
        pbix_file = _render_pbix_upload_panel(key_prefix)

    with st.container(border=True, key=f"{key_prefix}_form_section_content"):
        _render_form_section_heading("프로젝트 내용", "분석의 배경과 과정, 핵심 인사이트를 기록하세요.")
        project_body = render_project_body_editor(f"{key_prefix}_body", project_body_initial)

    cancelled = False
    if show_visibility_setting:
        visibility_col, actions_col = st.columns([2, 1], gap="large", vertical_alignment="bottom")
        with visibility_col, st.container(border=True, key=f"{key_prefix}_visibility_setting"):
            copy_col, toggle_col = st.columns([3, 1], gap="medium", vertical_alignment="center")
            with copy_col:
                st.markdown(
                    '<div class="folio-visibility-setting-copy"><strong>공개 설정</strong><span>공개를 끄면 목록과 검색에서 숨겨지고 작성자만 볼 수 있습니다.</span></div>',
                    unsafe_allow_html=True,
                )
            with toggle_col:
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
            "platform": platform_input,
            "project_body": project_body,
            "power_bi_url": power_bi_url_input,
            "report_url": etc_url_input,
            "github_url": github_url_input,
            "thumbnail_url": thumbnail_url_input,
            "thumbnail_mode": thumbnail_mode_input,
            "pbix_file": pbix_file,
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
                {_form_section_body_html(body)}
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def _form_section_body_html(body: str) -> str:
    if not body:
        return ""
    return f"<small>{html.escape(body)}</small>"


def _render_pbix_upload_panel(key_prefix: str):
    max_upload_mb = get_settings().pbix_max_upload_mb
    with st.container(border=True, key=f"{key_prefix}_form_section_pbix"):
        _render_form_section_heading(
            "Power BI PBIX 게시",
            "PBIX 파일을 업로드하면 FOLIO Workspace에 자동 게시합니다.",
        )
        st.warning("개인정보, 사내 데이터, 비공개 고객 정보가 포함된 PBIX는 업로드하지 마세요.")
        uploaded_file = st.file_uploader(
            "PBIX 파일 업로드",
            type=["pbix"],
            accept_multiple_files=False,
            help=f"최대 {max_upload_mb}MB까지 업로드할 수 있습니다.",
            key=f"{key_prefix}_pbix_file",
        )
        if uploaded_file is not None:
            st.success(f"{uploaded_file.name} 파일이 선택되었습니다.")
        return uploaded_file


def _project_platform_options() -> list[tuple[str, str]]:
    return [
        (PROJECT_PLATFORM_OTHER_KEY, "기타"),
        *((platform.key, platform.label) for platform in REFERENCE_PLATFORMS),
    ]


def project_type_for_platform(platform_key: str) -> str:
    project_types = {
        "powerbi": "powerbi",
        "tableau": "tableau",
        "datastudio": "looker",
        "streamlit": "streamlit",
    }
    return project_types.get(platform_key, "other")


def _render_platform_selector(key_prefix: str, platform_key: str) -> str:
    option_keys = [key for key, _ in _project_platform_options()]
    option_labels = {key: label for key, label in _project_platform_options()}
    selected_platform_key = platform_key if platform_key in option_keys else PROJECT_PLATFORM_OTHER_KEY
    return st.radio(
        "플랫폼",
        option_keys,
        index=option_keys.index(selected_platform_key),
        format_func=lambda key: option_labels[key],
        horizontal=True,
        key=f"{key_prefix}_platform",
    )


def _render_thumbnail_mode_selector(key_prefix: str, thumbnail_mode: str) -> str:
    selected_mode = thumbnail_mode if thumbnail_mode in PROJECT_THUMBNAIL_MODE_OPTIONS else THUMBNAIL_MODE_AUTO_COVER
    labels = {
        THUMBNAIL_MODE_AUTO_COVER: "기본 커버",
        THUMBNAIL_MODE_MANUAL_URL: "URL 직접 입력",
        THUMBNAIL_MODE_CAPTURE: "화면 자동 캡처",
    }
    return st.radio(
        "썸네일 설정",
        PROJECT_THUMBNAIL_MODE_OPTIONS,
        index=PROJECT_THUMBNAIL_MODE_OPTIONS.index(selected_mode),
        format_func=lambda mode: labels[mode],
        horizontal=True,
        key=f"{key_prefix}_thumbnail_mode",
    )


def _current_thumbnail_mode(key_prefix: str, thumbnail_mode: str) -> str:
    state_value = st.session_state.get(f"{key_prefix}_thumbnail_mode", thumbnail_mode)
    return state_value if state_value in PROJECT_THUMBNAIL_MODE_OPTIONS else THUMBNAIL_MODE_AUTO_COVER


def _current_thumbnail_url(key_prefix: str, thumbnail_url: str, thumbnail_mode: str) -> str:
    if thumbnail_mode == THUMBNAIL_MODE_AUTO_COVER:
        return ""
    if thumbnail_mode == THUMBNAIL_MODE_MANUAL_URL:
        return str(st.session_state.get(f"{key_prefix}_thumbnail_url", thumbnail_url) or "")
    return thumbnail_url


def _validate_optional_urls(
    power_bi_url: str,
    report_url: str,
    github_url: str,
    thumbnail_url: str,
    thumbnail_mode: str,
    *,
    has_pbix_upload: bool = False,
) -> str | None:
    if power_bi_url.strip() and normalize_power_bi_embed_url(power_bi_url) is None:
        return "Embed Code를 확인하세요. iframe 코드 또는 https URL을 입력해야 합니다."

    invalid_fields = []
    if report_url.strip() and normalize_optional_url(report_url) is None:
        invalid_fields.append("보고서 URL")
    if github_url.strip() and normalize_optional_url(github_url) is None:
        invalid_fields.append("GitHub URL")
    if thumbnail_mode == THUMBNAIL_MODE_MANUAL_URL and not thumbnail_url.strip():
        invalid_fields.append("썸네일 URL")
    elif thumbnail_url.strip() and normalize_optional_url(thumbnail_url) is None:
        invalid_fields.append("썸네일 URL")
    if thumbnail_mode == THUMBNAIL_MODE_CAPTURE and not has_pbix_upload and not (
        normalize_power_bi_embed_url(power_bi_url) or normalize_optional_url(report_url)
    ):
        return "자동 캡처를 사용하려면 Embed Code 또는 Web Application URL이 필요합니다."

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


def _validate_pbix_file(form_data: dict[str, Any]) -> str | None:
    pbix_file = form_data.get("pbix_file")
    if pbix_file is None:
        return None
    filename = str(getattr(pbix_file, "name", "") or "")
    if not filename.lower().endswith(".pbix"):
        return "PBIX 파일만 업로드할 수 있습니다."
    size = _uploaded_file_size(pbix_file)
    max_bytes = get_settings().pbix_max_upload_mb * 1024 * 1024
    if size > max_bytes:
        return f"PBIX 파일은 최대 {get_settings().pbix_max_upload_mb}MB까지 업로드할 수 있습니다."
    return None


def _uploaded_file_size(uploaded_file: Any) -> int:
    size = getattr(uploaded_file, "size", None)
    if isinstance(size, int):
        return size
    try:
        return len(uploaded_file.getbuffer())
    except Exception:
        return 0


def _normalize_tag_preview(value: str) -> list[str]:
    tags = []
    for tag in value.replace("#", "").split(","):
        normalized = tag.strip()
        if normalized and normalized not in tags:
            tags.append(normalized)
    return tags[:10]


def _normalized_tag(value: object) -> str:
    return str(value).strip().lower().replace(" ", "")


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
    platform_key: str = PROJECT_PLATFORM_OTHER_KEY,
    thumbnail_url: str = "",
) -> None:
    preview = {
        "title": title.strip() or "프로젝트명이 여기에 표시됩니다.",
        "one_liner": one_liner.strip(),
        "insights": plain_text(project_body),
        "tags": tags_with_platform(tags, platform_key),
        "view_count": 0,
        "like_count": 0,
        "thumbnail_url": thumbnail_url,
    }
    st.markdown(
        render_project_card_html(preview, fallback_text="프로젝트 소개가 여기에 표시됩니다."),
        unsafe_allow_html=True,
    )
