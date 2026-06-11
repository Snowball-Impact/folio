import html

import streamlit as st

from folio_app.components.layout import render_hero, render_placeholder_card
from folio_app.components.project_form import (
    PROJECT_BODY_TEMPLATE,
    build_project_payload,
    project_body_from_project,
    render_project_form,
    validate_project_form,
)
from folio_app.services.auth import get_current_user
from folio_app.services.profiles import get_profile
from folio_app.services.projects import (
    count_author_stats,
    create_project,
    delete_project,
    list_projects_by_author,
    update_project,
)


def render_submit() -> None:
    user = get_current_user()
    render_hero(
        "Submit",
        "새 프로젝트 등록",
        "당신의 데이터 분석 프로젝트를 포트폴리오로 공개하세요.",
    )

    if not user:
        st.warning("로그인이 필요합니다.")
        return

    form_data, submitted = render_project_form(
        "submit",
        title="",
        one_liner="",
        tags="",
        project_body_initial=PROJECT_BODY_TEMPLATE,
        power_bi_url="",
        report_url="",
        github_url="",
        thumbnail_url="",
        ai_summary="",
        submit_label="프로젝트 등록하기",
    )

    if not submitted:
        return

    parsed_body, missing, url_error = validate_project_form(form_data)
    if missing:
        st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
        return
    if url_error:
        st.error(url_error)
        return

    result = create_project(
        user["id"],
        build_project_payload(form_data, parsed_body),
    )

    if result.ok:
        st.query_params["page"] = "Gallery"
        st.query_params["project_id"] = result.project_id or ""
        st.rerun()
    else:
        st.error(result.message)


def render_my_portfolio() -> None:
    user = get_current_user()
    render_hero(
        "Portfolio",
        "내 포트폴리오",
        "내가 등록한 데이터 분석 프로젝트를 관리하세요.",
    )

    if not user:
        st.warning("로그인이 필요합니다.")
        return

    if st.button("새 프로젝트 등록하기", use_container_width=True):
        st.query_params["page"] = "Submit"
        st.rerun()

    projects = list_projects_by_author(user["id"])
    if not projects:
        st.info("아직 등록한 프로젝트가 없습니다.")
        return

    editing_project_id = st.session_state.get("editing_project_id")
    if editing_project_id:
        project = next((item for item in projects if item["id"] == editing_project_id), None)
        if project:
            _render_edit_project_form(user["id"], project)
            return
        st.session_state.pop("editing_project_id", None)

    for project in projects:
        title = html.escape(project.get("title") or "Untitled")
        body = f"조회 {project.get('view_count', 0)} / 좋아요 {project.get('like_count', 0)}\n상태: {'공개' if project.get('is_public') else '비공개'}"
        render_placeholder_card(title, body)

        view_col, edit_col, delete_col = st.columns(3)
        with view_col:
            if st.button("보기", key=f"portfolio_view_{project['id']}", use_container_width=True):
                st.query_params["page"] = "Gallery"
                st.query_params["project_id"] = project["id"]
                st.rerun()
        with edit_col:
            if st.button("수정", key=f"portfolio_edit_{project['id']}", use_container_width=True):
                st.session_state["editing_project_id"] = project["id"]
                st.rerun()
        with delete_col:
            confirm_delete = st.checkbox("삭제 확인", key=f"portfolio_confirm_delete_{project['id']}")
            if st.button(
                "삭제",
                key=f"portfolio_delete_{project['id']}",
                disabled=not confirm_delete,
                use_container_width=True,
            ):
                result = delete_project(project["id"], user["id"])
                if result.ok:
                    st.success(result.message)
                    st.rerun()
                else:
                    st.error(result.message)


def render_profile() -> None:
    user = get_current_user()
    render_hero(
        "Profile",
        "프로필",
        "내 계정과 포트폴리오 통계를 확인하세요.",
    )

    if not user:
        st.warning("로그인이 필요합니다.")
        return

    profile = get_profile(user["id"])
    if profile is None:
        st.info("프로필 정보를 불러오는 중 문제가 발생했습니다.")
        return

    data = profile or {}
    stats = count_author_stats(user["id"])
    name = html.escape(data.get("name") or user.get("email") or "")
    email = html.escape(data.get("email") or user.get("email") or "")
    organization = html.escape(data.get("organization") or "-")
    bio = html.escape(data.get("bio") or "-")
    body = (
        f"이메일: {email}\n"
        f"기관: {organization}\n"
        f"소개: {bio}\n"
        f"등록 프로젝트: {stats['project_count']}개\n"
        f"총 조회수: {stats['view_count']}"
    )
    render_placeholder_card(name, body)

    projects = list_projects_by_author(user["id"])
    if projects:
        st.markdown("### 작성 프로젝트")
        for project in projects:
            st.markdown(f"- {html.escape(project.get('title') or 'Untitled')} · 조회 {project.get('view_count', 0)}")


def _render_edit_project_form(author_id: str, project: dict) -> None:
    st.markdown("### 프로젝트 수정")
    if st.button("목록으로 돌아가기"):
        st.session_state.pop("editing_project_id", None)
        st.rerun()

    form_data, submitted = render_project_form(
        f"edit_{project['id']}",
        title=project.get("title") or "",
        one_liner=project.get("one_liner") or "",
        tags=", ".join(project.get("tags") or []),
        project_body_initial=project_body_from_project(project),
        power_bi_url=project.get("power_bi_url") or "",
        report_url=project.get("report_url") or "",
        github_url=project.get("github_url") or "",
        thumbnail_url=project.get("thumbnail_url") or "",
        ai_summary=project.get("ai_summary") or "",
        submit_label="수정 완료",
    )

    if not submitted:
        return

    parsed_body, missing, url_error = validate_project_form(form_data)
    if missing:
        st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
        return
    if url_error:
        st.error(url_error)
        return

    result = update_project(
        project["id"],
        author_id,
        build_project_payload(form_data, parsed_body),
    )

    if result.ok:
        st.session_state.pop("editing_project_id", None)
        st.success(result.message)
        st.rerun()
    else:
        st.error(result.message)
