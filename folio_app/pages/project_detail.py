from __future__ import annotations

import html

import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.layout import render_hero
from folio_app.components.project_comments import render_comments_section
from folio_app.components.project_detail_content import (
    project_report_sections,
    project_visual_context,
    render_project_report_sections,
    render_project_visual_panel,
)
from folio_app.components.share import project_action_group_html, render_project_share_handler
from folio_app.components.ui import clean_html, render_project_card_html
from folio_app.navigation import EDIT_PROJECT_QUERY_PARAM, navigate
from folio_app.services.auth import get_current_user
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    delete_project,
    get_project,
    increment_view_count,
    is_project_liked,
    set_project_liked,
)

_HOME_PAGE = "Home"


def render_loading_shell() -> None:
    render_hero(
        "프로젝트 상세",
        "프로젝트를 불러오고 있어요.",
        "곧 시각화와 프로젝트 설명이 이어서 표시됩니다.",
        image_html=_detail_loading_card_html(),
        class_name="folio-project-detail-hero folio-project-detail-loading-hero",
    )
    st.markdown(
        clean_html(
            """
            <section class="folio-detail-loading-content" aria-label="프로젝트 상세 로딩 중">
                <div class="folio-detail-loading-visual"></div>
                <div class="folio-detail-loading-panel">
                    <span class="folio-detail-loading-line folio-detail-loading-line-wide"></span>
                    <span class="folio-detail-loading-line"></span>
                    <span class="folio-detail-loading-line folio-detail-loading-line-short"></span>
                </div>
            </section>
            """
        ),
        unsafe_allow_html=True,
    )


def render(
    project_id: str,
    *,
    back_page: str = _HOME_PAGE,
    back_label: str = "홈 갤러리로 돌아가기",
    back_params: dict | None = None,
) -> None:
    back_params = back_params or {}
    notice = st.session_state.pop("project_notice", None)
    if notice:
        st.success(notice)

    loading_placeholder = st.empty()
    with loading_placeholder.container():
        render_loading_shell()

    try:
        project = get_project(project_id)
    except ProjectServiceError as exc:
        loading_placeholder.empty()
        st.error(str(exc))
        retry_col, back_col = st.columns(2)
        with retry_col:
            if st.button("다시 시도", key="retry_project_detail", use_container_width=True):
                clear_project_caches()
                st.rerun()
        with back_col:
            if st.button("목록으로 돌아가기", key="failed_detail_back", use_container_width=True):
                navigate(back_page, **back_params)
        return
    if project is None:
        loading_placeholder.empty()
        st.error("프로젝트를 찾을 수 없습니다.")
        if st.button("목록으로 돌아가기"):
            _clear_detail_query(back_page, back_params)
            st.rerun()
        return
    loading_placeholder.empty()

    track_event("view_item", {"item_id": project_id, "item_name": project.get("title") or ""})
    _track_share_open(project_id)

    like_count = project.get("like_count", 0) or 0
    user = get_current_user()
    like_error = st.session_state.pop("detail_like_error", None)

    hero_description = project.get("one_liner") or "프로젝트 소개가 없습니다."

    render_hero(
        "프로젝트 상세",
        project.get("title") or "Untitled",
        hero_description,
        image_html=_detail_hero_card_html(project),
        footer_actions=lambda: _render_hero_footer_actions(project, project_id, like_count, user, like_error),
        class_name="folio-project-detail-hero",
    )

    visual_context = project_visual_context(project)
    if visual_context["has_visual_panel"]:
        render_project_visual_panel(
            project,
            visual_context["power_bi_url"],
            visual_context["has_report"],
            visual_context["has_github"],
        )

    report_sections = project_report_sections(project)
    if not report_sections:
        st.info("아직 작성된 프로젝트 설명이 없습니다.")
    else:
        render_project_report_sections(report_sections)

    render_comments_section(project_id, user, project.get("author_id"))

    _render_back_to_gallery_action(back_page, back_label, back_params)
    _record_project_view(project_id)


def _detail_hero_card_html(project: dict) -> str:
    return render_project_card_html(project)


def _detail_loading_card_html() -> str:
    return clean_html(
        """
        <div class="folio-detail-loading-card" aria-hidden="true">
            <span class="folio-detail-loading-chip"></span>
            <span class="folio-detail-loading-title"></span>
            <span class="folio-detail-loading-line"></span>
            <span class="folio-detail-loading-line folio-detail-loading-line-short"></span>
            <div class="folio-detail-loading-metrics">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        """
    )


def _render_hero_footer_actions(
    project: dict,
    project_id: str,
    like_count: int,
    user: dict | None,
    like_error: str | None,
) -> None:
    if like_error:
        st.error(like_error)
    with st.container(
        border=False,
        key="detail_footer_row",
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="center",
        gap="small",
    ):
        st.markdown(_hero_meta_html(project), unsafe_allow_html=True)
        st.markdown(
            project_action_group_html(
                project_id,
                view_count=project.get("view_count", 0) or 0,
                is_public=bool(project.get("is_public")),
                comment_count=project.get("comment_count", 0) or 0,
            ),
            unsafe_allow_html=True,
        )
        _render_detail_like_button(project_id, like_count, user)
        _render_detail_edit_button(project, project_id, user)
        _render_detail_delete_button(project, project_id, user)
        render_project_share_handler(project_id)


def _render_back_to_gallery_action(back_page: str, back_label: str, back_params: dict) -> None:
    with st.container(
        border=False,
        key="detail_back_action_row",
        horizontal=True,
        horizontal_alignment="right",
        vertical_alignment="center",
    ):
        if st.button(f"← {back_label}", key="detail_content_back_button"):
            navigate(back_page, **back_params)


def _hero_meta_html(project: dict) -> str:
    author = project.get("author") or {}
    author_name = author.get("name") or "작성자"
    author_org = author.get("organization") or ""
    created_at = project.get("created_at") or ""
    org_html = (
        f'<span class="folio-detail-meta-item folio-detail-org"><small>소속</small><strong>{html.escape(author_org)}</strong></span>'
        if author_org
        else ""
    )
    return clean_html(f"""
    <div class="folio-detail-summary">
        <div class="folio-detail-meta-row">
            <span class="folio-detail-meta-item folio-detail-author"><small>작성자</small><strong>{html.escape(author_name)}</strong></span>
            {org_html}
            <span class="folio-detail-meta-item folio-detail-date"><small>등록일</small><strong>{created_at[:10] if created_at else '정보 없음'}</strong></span>
        </div>
    </div>
    """)


def _record_project_view(project_id: str) -> None:
    viewed_key = f"viewed_{project_id}"
    visitor_id = st.session_state.get("folio_visitor_id")
    if visitor_id and not st.session_state.get(viewed_key):
        view_result = increment_view_count(project_id, visitor_id)
        if view_result.ok:
            st.session_state[viewed_key] = True


def _render_detail_like_button(project_id: str, like_count: int, user: dict | None) -> None:
    if not user:
        if st.button(
            f"♡ 좋아요 {like_count}",
            key="detail_like_action",
            help="로그인 후 좋아요를 누를 수 있습니다.",
            use_container_width=False,
        ):
            navigate("Login")
        return

    try:
        liked = is_project_liked(project_id, user["id"])
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("좋아요 상태 다시 불러오기", key="retry_detail_like", use_container_width=True):
            clear_project_caches()
            st.rerun()
        return
    label = f"♥ 좋아요 {like_count}" if liked else f"♡ 좋아요 {like_count}"
    button_type = "primary" if liked else "secondary"
    if st.button(
        label,
        key="detail_like_action",
        type=button_type,
        use_container_width=False,
    ):
        result = set_project_liked(project_id, user["id"], not liked)
        if not result.ok:
            st.session_state["detail_like_error"] = result.message
        else:
            track_event("like" if not liked else "unlike", {"item_id": project_id})
        st.rerun()


def _render_detail_edit_button(project: dict, project_id: str, user: dict | None) -> None:
    if not _is_project_owner(project, user):
        return

    if st.button(
        "수정",
        key="detail_edit_project_action",
        icon=":material/edit:",
        use_container_width=False,
    ):
        navigate("My Page", **{EDIT_PROJECT_QUERY_PARAM: project_id})


def _render_detail_delete_button(project: dict, project_id: str, user: dict | None) -> None:
    if not _is_project_owner(project, user):
        return

    if st.button(
        "삭제",
        key="detail_delete_project_action",
        icon=":material/delete:",
        use_container_width=False,
    ):
        _confirm_detail_project_deletion(project, project_id, user["id"])


@st.dialog("프로젝트 삭제")
def _confirm_detail_project_deletion(project: dict, project_id: str, author_id: str) -> None:
    _render_detail_project_deletion_dialog(project, project_id, author_id)


def _render_detail_project_deletion_dialog(project: dict, project_id: str, author_id: str) -> None:
    title = project.get("title") or "제목 없는 프로젝트"
    st.write(f"‘{title}’ 프로젝트를 삭제할까요?")
    st.caption("삭제한 프로젝트는 복구할 수 없습니다.")

    cancel_col, delete_col = st.columns(2)
    with cancel_col:
        if st.button("취소", key=f"detail_delete_cancel_{project_id}", use_container_width=True):
            st.rerun()
    with delete_col:
        if st.button(
            "삭제하기",
            key=f"detail_delete_confirm_{project_id}",
            type="primary",
            use_container_width=True,
        ):
            result = delete_project(project_id, author_id)
            if result.ok:
                st.session_state["home_notice"] = result.message
                navigate("Home")
            else:
                st.error(result.message)


def _is_project_owner(project: dict, user: dict | None) -> bool:
    return bool(user and project.get("author_id") == user.get("id"))


def _track_share_open(project_id: str) -> None:
    if st.query_params.get("utm_medium") != "share":
        return
    if st.query_params.get("utm_campaign") != "project_share":
        return

    tracked_key = f"tracked_share_open_{project_id}"
    if st.session_state.get(tracked_key):
        return

    st.session_state[tracked_key] = True
    track_event("project_share_open", {"item_id": project_id, "source": "copied_link"})


def _clear_detail_query(back_page: str = _HOME_PAGE, back_params: dict | None = None) -> None:
    navigate(back_page, **(back_params or {}))
