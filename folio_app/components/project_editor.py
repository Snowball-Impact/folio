"""Submit/edit project form flows."""

from __future__ import annotations

from dataclasses import replace
import time
import streamlit as st

from folio_app.config import get_settings
from folio_app.components.analytics import track_event
from folio_app.components.dashboard import powerbi_report_html
from folio_app.components.project_body import PROJECT_BODY_TEMPLATE, project_body_from_project
from folio_app.components.project_form import (
    build_project_payload,
    hero_preview_project,
    render_project_form,
    validate_project_form,
)
from folio_app.components.layout import render_hero
from folio_app.components.ui import render_project_card_html
from folio_app.navigation import navigate
from folio_app.services.project_normalizers import THUMBNAIL_MODE_CAPTURE
from folio_app.services.project_drafts import (
    apply_pending_draft_clear,
    clear_project_draft,
    load_project_draft,
    save_project_draft,
)
from folio_app.services.powerbi import (
    PowerBIServiceError,
    delete_powerbi_report_for_project,
    generate_embed_token,
    get_powerbi_report_for_project,
    publish_pbix_for_project,
)
from folio_app.services.project_thumbnails import capture_project_thumbnail_from_html, upload_project_thumbnail_file
from folio_app.services.projects import clear_project_caches, create_project, update_project
from folio_app.services.project_references import reference_platform_for_project


def render_submit_project_form(user_id: str) -> None:
    draft_id = "submit"
    widget_prefix = "submit"
    apply_pending_draft_clear(st.session_state, user_id, draft_id)
    draft = load_project_draft(st.session_state, user_id, draft_id, _submit_project_defaults())
    render_hero(
        "Submit",
        "새 프로젝트 등록",
        "당신의 데이터 분석 프로젝트를 포트폴리오로 공개하세요.",
        image_html=render_project_card_html(hero_preview_project(draft, widget_prefix)),
        class_name="folio-project-detail-hero folio-submit-preview-hero",
    )

    form_data, submitted, discarded = render_project_form(
        widget_prefix,
        title=draft["title"],
        one_liner=draft["one_liner"],
        tags=draft["tags"],
        project_body_initial=draft["project_body"],
        power_bi_url=draft["power_bi_url"],
        github_url=draft["github_url"],
        etc_url=draft["report_url"],
        submit_label="프로젝트 등록하기",
        platform_key=draft["platform"],
        thumbnail_url=draft["thumbnail_url"],
        thumbnail_mode=draft["thumbnail_mode"],
        allow_pbix_upload=True,
        secondary_label="초안 지우기",
    )
    save_project_draft(st.session_state, user_id, draft_id, form_data)

    if discarded:
        clear_project_draft(st.session_state, user_id, draft_id, widget_prefix)
        st.rerun()

    if not submitted:
        return

    parsed_body = _validated_project_body(form_data)
    if parsed_body is None:
        return

    payload = build_project_payload(form_data, parsed_body)
    pbix_file = form_data.get("pbix_file")
    if pbix_file is not None:
        if payload.get("thumbnail_mode") == THUMBNAIL_MODE_CAPTURE:
            payload["skip_thumbnail_capture"] = True
        powerbi_result = _create_and_publish_powerbi_project(user_id, payload, pbix_file)
        if powerbi_result is None:
            return
        if powerbi_result.ok:
            _apply_uploaded_thumbnail_if_requested(powerbi_result.project_id, form_data)
            track_event("pbix_import_success", {"item_id": powerbi_result.project_id})
            clear_project_draft(st.session_state, user_id, draft_id, widget_prefix)
            st.session_state["project_notice"] = powerbi_result.message
            navigate("Home", project_id=powerbi_result.project_id)
        else:
            track_event("pbix_import_failed", {"item_id": powerbi_result.project_id})
            _show_operation_error(powerbi_result.message)
        return

    result = _run_with_thumbnail_progress(
        form_data,
        lambda progress_callback: create_project(user_id, payload, progress_callback=progress_callback),
        "프로젝트를 등록하고 썸네일을 자동 캡처 중입니다.",
    )

    if result.ok:
        _apply_uploaded_thumbnail_if_requested(result.project_id, form_data)
        track_event("project_submit", {"item_id": result.project_id})
        clear_project_draft(st.session_state, user_id, draft_id, widget_prefix)
        st.session_state["project_notice"] = result.message
        navigate("Home", project_id=result.project_id)
    else:
        _show_operation_error(result.message)


def render_edit_project_form(author_id: str, project: dict) -> None:
    draft_id = f"edit:{project['id']}"
    widget_prefix = f"edit_{project['id']}"
    apply_pending_draft_clear(st.session_state, author_id, draft_id)
    draft = load_project_draft(st.session_state, author_id, draft_id, _edit_project_defaults(project))
    has_powerbi_report = _has_powerbi_report(project)
    render_hero(
        "Edit",
        "프로젝트 수정",
        "프로젝트 정보와 대표 썸네일을 업데이트하세요.",
        image_html=render_project_card_html(hero_preview_project(draft, widget_prefix)),
        class_name="folio-project-detail-hero folio-submit-preview-hero",
    )

    form_data, submitted, cancelled = render_project_form(
        widget_prefix,
        title=draft["title"],
        one_liner=draft["one_liner"],
        tags=draft["tags"],
        project_body_initial=draft["project_body"],
        power_bi_url=draft["power_bi_url"],
        github_url=draft["github_url"],
        etc_url=draft["report_url"],
        platform_key=draft["platform"],
        thumbnail_url=draft["thumbnail_url"],
        existing_thumbnail_url=project.get("thumbnail_url") or "",
        thumbnail_mode=draft["thumbnail_mode"],
        has_powerbi_report=has_powerbi_report,
        is_public=bool(draft["is_public"]),
        show_visibility_setting=True,
        allow_pbix_upload=True,
        submit_label="수정 완료",
        secondary_label="목록으로 돌아가기",
    )
    save_project_draft(st.session_state, author_id, draft_id, form_data)

    if cancelled:
        clear_project_draft(st.session_state, author_id, draft_id, widget_prefix)
        st.session_state.pop("editing_project_id", None)
        navigate("My Page")

    if not submitted:
        return

    parsed_body = _validated_project_body(form_data)
    if parsed_body is None:
        return

    payload = build_project_payload(form_data, parsed_body)
    pbix_file = form_data.get("pbix_file")
    if pbix_file is not None:
        payload["project_type"] = "powerbi"
        payload["status"] = "processing"
        payload["embed_status"] = "external_only"
        if payload.get("thumbnail_mode") == THUMBNAIL_MODE_CAPTURE:
            payload["skip_thumbnail_capture"] = True
    result = _run_with_thumbnail_progress(
        form_data,
        lambda progress_callback: update_project(
            project["id"],
            author_id,
            payload,
            progress_callback=progress_callback,
        ),
        "프로젝트를 수정하고 썸네일을 자동 캡처 중입니다.",
    )

    if result.ok:
        if pbix_file is not None:
            powerbi_result = _publish_replacement_pbix(project["id"], pbix_file, payload)
            if powerbi_result is None:
                return
            if not powerbi_result.ok:
                _show_operation_error(powerbi_result.message)
                return
            _apply_uploaded_thumbnail_if_requested(project["id"], form_data)
            result = powerbi_result
        elif form_data.get("delete_pbix"):
            try:
                delete_powerbi_report_for_project(project["id"])
                clear_project_caches()
            except PowerBIServiceError as exc:
                _show_operation_error(str(exc))
                return
        else:
            _apply_uploaded_thumbnail_if_requested(project["id"], form_data)
        clear_project_draft(st.session_state, author_id, draft_id, widget_prefix)
        st.session_state.pop("editing_project_id", None)
        st.session_state["project_notice"] = result.message
        navigate("Home", project_id=project["id"])
    else:
        _show_operation_error(result.message)


def _submit_project_defaults() -> dict:
    return {
        "title": "",
        "one_liner": "",
        "tags": "",
        "project_body": PROJECT_BODY_TEMPLATE,
        "power_bi_url": "",
        "github_url": "",
        "report_url": "",
        "platform": "other",
        "thumbnail_url": "",
        "thumbnail_mode": "auto_cover",
        "is_public": True,
    }


def _edit_project_defaults(project: dict) -> dict:
    return {
        "title": project.get("title") or "",
        "one_liner": project.get("one_liner") or "",
        "tags": ", ".join(project.get("tags") or []),
        "project_body": project_body_from_project(project),
        "power_bi_url": project.get("power_bi_url") or "",
        "github_url": project.get("github_url") or "",
        "report_url": project.get("report_url") or "",
        "platform": reference_platform_for_project(project) or "other",
        "thumbnail_url": project.get("thumbnail_url") or "",
        "thumbnail_mode": project.get("thumbnail_mode") or ("manual_url" if project.get("thumbnail_url") else "auto_cover"),
        "is_public": bool(project.get("is_public")),
    }


def _validated_project_body(form_data: dict[str, str]) -> dict[str, str] | None:
    parsed_body, missing, url_error = validate_project_form(form_data)
    if missing:
        _show_operation_error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
        return None
    if url_error:
        _show_operation_error(url_error)
        return None
    return parsed_body


def _show_operation_error(message: str) -> None:
    with st.container(border=True, key=f"project_operation_error_{abs(hash(message))}"):
        st.markdown('<div class="folio-operation-title">처리 결과</div>', unsafe_allow_html=True)
        st.error(message)


def _create_operation_progress(key: str, initial_value: int, text: str):
    panel = st.container(border=True, key=f"{key}_operation_panel")
    with panel:
        st.markdown('<div class="folio-operation-title">작업 진행</div>', unsafe_allow_html=True)
        progress = st.progress(initial_value, text=text)
    return panel, progress


def _run_with_thumbnail_progress(form_data: dict, action, message: str):
    if form_data.get("thumbnail_mode") != THUMBNAIL_MODE_CAPTURE:
        return action(None)

    _, progress = _create_operation_progress("thumbnail_capture", 12, message)
    try:
        def update_progress(value: int, text: str) -> None:
            progress.progress(value, text=text)

        progress.progress(28, text="프로젝트 정보를 저장하는 중입니다.")
        result = action(update_progress)
        progress.progress(100, text="썸네일 처리 요청이 완료되었습니다.")
        return result
    finally:
        progress.empty()


def _apply_uploaded_thumbnail_if_requested(project_id: str | None, form_data: dict) -> None:
    if not project_id:
        return
    uploaded_thumbnail = form_data.get("thumbnail_file")
    if uploaded_thumbnail is None:
        return
    result = upload_project_thumbnail_file(project_id, uploaded_thumbnail)
    if not result.ok:
        st.warning("프로젝트는 저장됐지만 썸네일 업로드에 실패했습니다. 이미지를 확인한 뒤 다시 시도하세요.")
    else:
        clear_project_caches()


def _has_powerbi_report(project: dict) -> bool:
    if project.get("project_type") == "powerbi" and project.get("power_bi_url"):
        return True
    try:
        return get_powerbi_report_for_project(project["id"]) is not None
    except PowerBIServiceError:
        return False


def _publish_replacement_pbix(project_id: str, pbix_file, payload: dict | None = None):
    settings = get_settings()
    if not settings.is_powerbi_configured:
        _show_operation_error("Power BI 게시 환경 변수가 설정되지 않았습니다.")
        return None

    _, progress = _create_operation_progress(
        "pbix_replacement",
        20,
        "새 PBIX 파일을 Power BI Workspace에 게시하는 중입니다.",
    )
    try:
        def update_progress(value: int, text: str) -> None:
            progress.progress(value, text=text)

        pbix_bytes = bytes(pbix_file.getbuffer())
        result = publish_pbix_for_project(
            project_id,
            pbix_bytes,
            pbix_file.name,
            settings=settings,
            progress_callback=update_progress,
        )
        if result.ok:
            capture_result = _capture_powerbi_thumbnail_if_requested(
                project_id,
                payload or {},
                result,
                update_progress,
            )
            result = _powerbi_result_with_thumbnail_message(result, capture_result)
        progress.progress(100, text="PBIX 교체 요청이 완료되었습니다.")
        if result.ok:
            track_event("pbix_import_success", {"item_id": result.project_id})
            clear_project_caches()
        else:
            track_event("pbix_import_failed", {"item_id": result.project_id})
        return result
    finally:
        progress.empty()


def _create_and_publish_powerbi_project(user_id: str, payload: dict, pbix_file):
    settings = get_settings()
    if not settings.is_powerbi_configured:
        _show_operation_error("Power BI 게시 환경 변수가 설정되지 않았습니다.")
        return None

    payload = dict(payload)
    payload["project_type"] = "powerbi"
    payload["status"] = "processing"
    payload["embed_status"] = "external_only"
    if payload.get("thumbnail_mode") == THUMBNAIL_MODE_CAPTURE:
        payload["skip_thumbnail_capture"] = True

    panel, progress = _create_operation_progress("pbix_create", 10, "Power BI 프로젝트를 등록하는 중입니다.")
    try:
        def update_progress(value: int, text: str) -> None:
            progress.progress(value, text=text)

        create_result = create_project(user_id, payload)
        if not create_result.ok or not create_result.project_id:
            with panel:
                st.error(create_result.message)
            return None
        progress.progress(35, text="PBIX 파일을 Power BI Workspace에 게시하는 중입니다.")
        pbix_bytes = bytes(pbix_file.getbuffer())
        result = publish_pbix_for_project(
            create_result.project_id,
            pbix_bytes,
            pbix_file.name,
            settings=settings,
            progress_callback=update_progress,
        )
        if result.ok:
            capture_result = _capture_powerbi_thumbnail_if_requested(
                result.project_id,
                payload,
                result,
                update_progress,
            )
            result = _powerbi_result_with_thumbnail_message(result, capture_result)
            clear_project_caches()
        progress.progress(100, text="Power BI 게시 요청이 완료되었습니다.")
        return result
    finally:
        progress.empty()


def _capture_powerbi_thumbnail_if_requested(project_id: str, payload: dict, publish_result, progress_callback):
    if payload.get("thumbnail_mode") != THUMBNAIL_MODE_CAPTURE:
        return None
    if not (publish_result.report_id and publish_result.dataset_id and publish_result.embed_url):
        return None
    _wait_for_powerbi_report_ready(get_settings().powerbi_capture_ready_wait_seconds, progress_callback)
    token_payload = generate_embed_token(publish_result.report_id, publish_result.dataset_id)
    embed_token = token_payload.get("token")
    if not embed_token:
        return None
    capture_html = powerbi_report_html(publish_result.report_id, publish_result.embed_url, str(embed_token))
    return capture_project_thumbnail_from_html(project_id, capture_html, progress_callback=progress_callback)


def _wait_for_powerbi_report_ready(seconds: int, progress_callback) -> None:
    wait_seconds = max(int(seconds or 0), 0)
    for second in range(wait_seconds):
        if progress_callback is not None:
            progress = 40 + int(((second + 1) / wait_seconds) * 4)
            remaining_seconds = wait_seconds - second
            progress_callback(progress, f"Power BI 보고서 렌더링 준비를 기다리는 중입니다. {remaining_seconds}/{wait_seconds}초")
        time.sleep(1)


def _powerbi_result_with_thumbnail_message(result, capture_result):
    if capture_result is None or getattr(capture_result, "skipped", False):
        return result
    if getattr(capture_result, "ok", False):
        return replace(result, message=f"{result.message} 썸네일 캡처도 완료되었습니다.")
    return replace(result, message=f"{result.message} 썸네일은 기본 커버로 표시됩니다.")
