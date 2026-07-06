from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.layout import render_hero
from folio_app.components.ui import is_http_url, render_project_cover_html
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

    viewed_key = f"viewed_{project_id}"
    if not st.session_state.get(viewed_key):
        increment_view_count(project_id)
        st.session_state[viewed_key] = True

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

    author = project.get("author") or {}
    created_at = project.get("created_at") or ""
    author_name = author.get("name") or "작성자"
    author_org = author.get("organization") or ""

    like_count = project.get("like_count", 0) or 0
    view_count = project.get("view_count", 0) or 0
    user = get_current_user()
    like_error = st.session_state.pop("detail_like_error", None)

    hero_description = project.get("one_liner") or "프로젝트 소개가 없습니다."
    is_public = bool(project.get("is_public"))
    visibility_label = "🔒 비공개" if not is_public else "🔓 공개"

    hero_meta_html = f"""
        <div class="folio-detail-meta-row">
            <span class="folio-detail-meta-item folio-detail-author"><small>작성자</small><strong>{html.escape(author_name)}</strong></span>
            {f'<span class="folio-detail-meta-item folio-detail-org"><small>소속</small><strong>{html.escape(author_org)}</strong></span>' if author_org else ''}
            <span class="folio-detail-meta-item folio-detail-date"><small>등록일</small><strong>{created_at[:10] if created_at else '정보 없음'}</strong></span>
        </div>
        """

    def _render_hero_footer_actions() -> None:
        if like_error:
            st.error(like_error)
        meta_col, view_col, like_col, visibility_col = st.columns([3.2, 1, 1, 1], gap="small")

        with meta_col:
            st.markdown(hero_meta_html, unsafe_allow_html=True)

        with view_col:
            st.markdown(
                f'<div class="folio-detail-stat" aria-label="조회수 {view_count}"><span>조회수</span><strong>{view_count:,}</strong></div>',
                unsafe_allow_html=True,
            )

        with like_col:
            _render_detail_like_button(project_id, like_count, user)

        with visibility_col:
            st.markdown(
                f'<div class="folio-detail-stat folio-detail-visibility-stat" aria-label="공개 상태 {visibility_label}"><strong>{visibility_label}</strong></div>',
                unsafe_allow_html=True,
            )

    render_hero(
        "프로젝트 상세",
        project.get("title") or "Untitled",
        hero_description,
        image_html=render_project_cover_html(project),
        footer_actions=_render_hero_footer_actions,
        class_name="folio-project-detail-hero",
    )

    has_report = is_http_url(project.get("report_url"))
    has_github = is_http_url(project.get("github_url"))
    power_bi_url = normalize_power_bi_embed_url(project.get("power_bi_url"))
    has_sidebar = bool(power_bi_url or project.get("power_bi_url") or has_report or has_github)

    if has_sidebar:
        content_col, side_col = st.columns([1.75, 1])
    else:
        content_col = st.container()
        side_col = None

    with content_col:
        sections = [
            ("📋 문제 정의", project.get("problem")),
            ("📊 사용 데이터", project.get("dataset")),
            ("🔍 분석 과정", project.get("process")),
            ("💡 핵심 인사이트", project.get("insights")),
        ]
        if not any(body for _, body in sections):
            st.info("아직 작성된 프로젝트 설명이 없습니다.")
        for title, body in sections:
            _render_section(title, body)

    if side_col is not None:
        with side_col, st.container(border=False, key="project_detail_sidebar"):
            _render_project_sidebar(project, power_bi_url, has_report, has_github)
    else:
        if st.button("← 목록으로 돌아가기", key="detail_content_back_button"):
            navigate(_HOME_PAGE)


def _render_project_sidebar(
    project: dict,
    power_bi_url: str | None,
    has_report: bool,
    has_github: bool,
) -> None:
    if power_bi_url:
        st.markdown(
            '<div class="folio-sidebar-heading"><h2>대시보드</h2></div>',
            unsafe_allow_html=True,
        )
        components.html(
                f"""
                <style>
                    html,
                    body {{
                        margin: 0;
                        overflow: hidden;
                        padding: 0;
                    }}
                    .folio-dashboard-frame {{
                        aspect-ratio: 16 / 12;
                        position: relative;
                        width: 100%;
                    }}
                    .folio-dashboard-placeholder {{
                        align-items: center;
                        background: #f4f7fc;
                        color: #60708f;
                        display: flex;
                        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                        font-size: 14px;
                        height: 100%;
                        inset: 0;
                        justify-content: center;
                        position: absolute;
                        width: 100%;
                        z-index: 1;
                    }}
                    .folio-dashboard-iframe {{
                        background: #ffffff;
                        border: 0;
                        height: 100%;
                        inset: 0;
                        position: absolute;
                        width: 100%;
                        z-index: 2;
                    }}
                </style>
                <div class="folio-dashboard-frame">
                    <div class="folio-dashboard-placeholder" id="folio-dashboard-placeholder">
                        대시보드 불러오는 중...
                    </div>
                    <iframe
                        title="Embedded dashboard"
                        src="{html.escape(power_bi_url, quote=True)}"
                        frameborder="0"
                        allowFullScreen="true"
                        class="folio-dashboard-iframe"
                        onload="var placeholder=document.getElementById('folio-dashboard-placeholder'); if (placeholder) placeholder.style.display='none';">
                    </iframe>
                </div>
                """,
            height=270,
        )
        st.caption("화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.")
        st.link_button("대시보드 새 탭에서 열기 ↗", power_bi_url, use_container_width=True)
    elif project.get("power_bi_url"):
        st.warning("Power BI 임베드 주소를 확인하세요. iframe 코드 또는 https URL의 src 값이 필요합니다.")

    if has_report or has_github:
        st.markdown(
            '<div class="folio-sidebar-heading folio-sidebar-resources"><h2>첨부 자료</h2></div>',
            unsafe_allow_html=True,
        )
        if has_report:
            st.link_button("보고서 보기 ↗", project["report_url"], use_container_width=True)
        if has_github:
            st.link_button("GitHub 저장소 보기 ↗", project["github_url"], use_container_width=True)

    if st.button("← 목록으로 돌아가기", key="detail_visual_back_button", use_container_width=True):
        navigate(_HOME_PAGE)


def _render_detail_like_button(project_id: str, like_count: int, user: dict | None) -> None:
    if not user:
        if st.button(
            f"♡ {like_count}",
            key="detail_like_action",
            help="로그인 후 좋아요를 누를 수 있습니다.",
            use_container_width=True,
        ):
            navigate("Login")
        return

    liked = is_project_liked(project_id, user["id"])
    label = f"♥ {like_count}" if liked else f"♡ {like_count}"
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
        st.rerun()


def _render_section(title: str, body: str | None) -> None:
    if not body:
        return
    st.markdown(
        f"""
        <div class="folio-detail-section">
            <h3 class="folio-detail-section-title">{html.escape(title)}</h3>
            <div class="folio-detail-section-content">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(sanitize_project_html(body), unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


def _clear_detail_query() -> None:
    navigate(_HOME_PAGE)
