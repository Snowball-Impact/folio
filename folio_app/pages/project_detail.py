from __future__ import annotations

import html

import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.dashboard import render_embedded_dashboard
from folio_app.components.layout import render_hero
from folio_app.components.share import render_project_action_group
from folio_app.components.ui import clean_html, is_http_url, render_project_cover_html
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.project_content import sanitize_project_html
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    get_project,
    increment_view_count,
    is_project_liked,
    normalize_power_bi_embed_url,
    set_project_liked,
)

_HOME_PAGE = "Home"


def render(project_id: str) -> None:
    notice = st.session_state.pop("project_notice", None)
    if notice:
        st.success(notice)

    _record_project_view(project_id)

    try:
        project = get_project(project_id)
    except ProjectServiceError as exc:
        st.error(str(exc))
        retry_col, back_col = st.columns(2)
        with retry_col:
            if st.button("다시 시도", key="retry_project_detail", use_container_width=True):
                clear_project_caches()
                st.rerun()
        with back_col:
            if st.button("목록으로 돌아가기", key="failed_detail_back", use_container_width=True):
                navigate(_HOME_PAGE)
        return
    if project is None:
        st.error("프로젝트를 찾을 수 없습니다.")
        if st.button("목록으로 돌아가기"):
            _clear_detail_query()
            st.rerun()
        return

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
        image_html=render_project_cover_html(project),
        footer_actions=lambda: _render_hero_footer_actions(project, project_id, like_count, user, like_error),
        class_name="folio-project-detail-hero",
    )

    visual_context = _project_visual_context(project)
    if visual_context["has_visual_panel"]:
        _render_project_visual_panel(
            project,
            visual_context["power_bi_url"],
            visual_context["has_report"],
            visual_context["has_github"],
        )

    report_sections = _project_report_sections(project)
    if not report_sections:
        st.info("아직 작성된 프로젝트 설명이 없습니다.")
    else:
        _render_sections(report_sections)

    if st.button("← 홈 갤러리로 돌아가기", key="detail_content_back_button"):
        navigate(_HOME_PAGE)


def _render_hero_footer_actions(
    project: dict,
    project_id: str,
    like_count: int,
    user: dict | None,
    like_error: str | None,
) -> None:
    if like_error:
        st.error(like_error)
    meta_col, controls_col = st.columns(
        [4.4, 3.6],
        gap="medium",
        vertical_alignment="center",
    )

    with meta_col:
        st.markdown(_hero_meta_html(project), unsafe_allow_html=True)

    with controls_col:
        with st.container(border=False, key="detail_footer_controls"):
            action_col, like_col = st.columns(
                [1.9, 0.72],
                gap="small",
                vertical_alignment="center",
            )

            with action_col:
                render_project_action_group(
                    project_id,
                    view_count=project.get("view_count", 0) or 0,
                    is_public=bool(project.get("is_public")),
                )

            with like_col:
                _render_detail_like_button(project_id, like_count, user)


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


def _render_project_visual_panel(
    project: dict,
    power_bi_url: str | None,
    has_report: bool,
    has_github: bool,
) -> None:
    with st.container(border=False, key="project_detail_visual"):
        st.markdown(
            '<div class="folio-visual-heading"><h2>대표 결과물</h2></div>',
            unsafe_allow_html=True,
        )
        if power_bi_url:
            render_embedded_dashboard(power_bi_url)
            st.caption("화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.")
        elif project.get("power_bi_url"):
            st.warning("Power BI 임베드 주소를 확인하세요. iframe 코드 또는 https URL의 src 값이 필요합니다.")

        actions = _project_resource_actions(project, power_bi_url, has_report, has_github)
        if actions:
            action_cols = st.columns(len(actions), gap="medium")
            for action_col, (label, url) in zip(action_cols, actions):
                with action_col:
                    st.link_button(label, url, use_container_width=True)


def _project_visual_context(project: dict) -> dict[str, object]:
    power_bi_url = normalize_power_bi_embed_url(project.get("power_bi_url"))
    has_report = is_http_url(project.get("report_url"))
    has_github = is_http_url(project.get("github_url"))
    return {
        "power_bi_url": power_bi_url,
        "has_report": has_report,
        "has_github": has_github,
        "has_visual_panel": bool(power_bi_url or project.get("power_bi_url") or has_report or has_github),
    }


def _project_resource_actions(
    project: dict,
    power_bi_url: str | None,
    has_report: bool,
    has_github: bool,
) -> list[tuple[str, str]]:
    actions = []
    if power_bi_url:
        actions.append(("대시보드 열기 ↗", power_bi_url))
    if has_report:
        actions.append(("보고서 보기 ↗", project["report_url"]))
    if has_github:
        actions.append(("GitHub 보기 ↗", project["github_url"]))
    return actions


def _render_detail_like_button(project_id: str, like_count: int, user: dict | None) -> None:
    if not user:
        if st.button(
            f"♡ 좋아요 {like_count}",
            key="detail_like_action",
            help="로그인 후 좋아요를 누를 수 있습니다.",
            use_container_width=True,
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
        use_container_width=True,
    ):
        result = set_project_liked(project_id, user["id"], not liked)
        if not result.ok:
            st.session_state["detail_like_error"] = result.message
        else:
            track_event("like" if not liked else "unlike", {"item_id": project_id})
        st.rerun()


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


def _project_report_sections(project: dict) -> list[str]:
    return [
        body
        for body in [
            project.get("problem"),
            project.get("dataset"),
            project.get("process"),
            project.get("insights"),
        ]
        if body
    ]


def _render_sections(sections: list[str]) -> None:
    st.markdown(
        _project_report_html(sections),
        unsafe_allow_html=True,
    )


def _project_report_html(sections: list[str]) -> str:
    section_html = "".join(_project_report_section_html(body) for body in sections)
    return clean_html(
        '<article class="folio-detail-content-card">'
        '<header class="folio-detail-content-heading"><h2>프로젝트 리포트</h2></header>'
        f"{section_html}</article>"
    )


def _project_report_section_html(body: str) -> str:
    return (
        '<section class="folio-detail-section">'
        f'<div class="folio-detail-section-content">{sanitize_project_html(body)}</div>'
        "</section>"
    )


def _clear_detail_query() -> None:
    navigate(_HOME_PAGE)
