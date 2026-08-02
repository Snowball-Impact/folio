"""Submit/edit project form flows."""

from __future__ import annotations

import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.project_body import PROJECT_BODY_TEMPLATE, project_body_from_project
from folio_app.components.project_form import (
    build_project_payload,
    render_project_form,
    validate_project_form,
)
from folio_app.navigation import navigate
from folio_app.services.project_drafts import (
    apply_pending_draft_clear,
    clear_project_draft,
    load_project_draft,
    save_project_draft,
)
from folio_app.services.projects import create_project, update_project


def render_submit_project_form(user_id: str) -> None:
    draft_id = "submit"
    widget_prefix = "submit"
    apply_pending_draft_clear(st.session_state, user_id, draft_id)
    draft = load_project_draft(st.session_state, user_id, draft_id, _submit_project_defaults())

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

    result = create_project(
        user_id,
        build_project_payload(form_data, parsed_body),
    )

    if result.ok:
        track_event("project_submit", {"item_id": result.project_id})
        clear_project_draft(st.session_state, user_id, draft_id, widget_prefix)
        st.session_state["project_notice"] = result.message
        navigate("Home", project_id=result.project_id)
    else:
        st.error(result.message)


def render_edit_project_form(author_id: str, project: dict) -> None:
    st.markdown("### 프로젝트 수정")

    draft_id = f"edit:{project['id']}"
    widget_prefix = f"edit_{project['id']}"
    apply_pending_draft_clear(st.session_state, author_id, draft_id)
    draft = load_project_draft(st.session_state, author_id, draft_id, _edit_project_defaults(project))

    form_data, submitted, cancelled = render_project_form(
        widget_prefix,
        title=draft["title"],
        one_liner=draft["one_liner"],
        tags=draft["tags"],
        project_body_initial=draft["project_body"],
        power_bi_url=draft["power_bi_url"],
        github_url=draft["github_url"],
        etc_url=draft["report_url"],
        thumbnail_url=draft["thumbnail_url"],
        is_public=bool(draft["is_public"]),
        show_visibility_setting=True,
        submit_label="수정 완료",
        secondary_label="목록으로 돌아가기",
    )
    save_project_draft(st.session_state, author_id, draft_id, form_data)

    if cancelled:
        clear_project_draft(st.session_state, author_id, draft_id, widget_prefix)
        st.session_state.pop("editing_project_id", None)
        st.rerun()

    if not submitted:
        return

    parsed_body = _validated_project_body(form_data)
    if parsed_body is None:
        return

    result = update_project(
        project["id"],
        author_id,
        build_project_payload(form_data, parsed_body),
    )

    if result.ok:
        clear_project_draft(st.session_state, author_id, draft_id, widget_prefix)
        st.session_state.pop("editing_project_id", None)
        st.session_state["portfolio_notice"] = result.message
        st.rerun()
    else:
        st.error(result.message)


def _submit_project_defaults() -> dict:
    return {
        "title": "",
        "one_liner": "",
        "tags": "",
        "project_body": PROJECT_BODY_TEMPLATE,
        "power_bi_url": "",
        "github_url": "",
        "report_url": "",
        "thumbnail_url": "",
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
        "thumbnail_url": project.get("thumbnail_url") or "",
        "is_public": bool(project.get("is_public")),
    }


def _validated_project_body(form_data: dict[str, str]) -> dict[str, str] | None:
    parsed_body, missing, url_error = validate_project_form(form_data)
    if missing:
        st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
        return None
    if url_error:
        st.error(url_error)
        return None
    return parsed_body
