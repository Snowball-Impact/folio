from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.analytics import track_event
from folio_app.components.layout import render_hero
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
    visibility_label = "비공개" if not is_public else "공개"

    hero_meta_html = f"""
        <div class="folio-detail-summary">
          <div class="folio-detail-meta-row">
            <span class="folio-detail-meta-item folio-detail-author"><small>작성자</small><strong>{html.escape(author_name)}</strong></span>
            {f'<span class="folio-detail-meta-item folio-detail-org"><small>소속</small><strong>{html.escape(author_org)}</strong></span>' if author_org else ''}
            <span class="folio-detail-meta-item folio-detail-date"><small>등록일</small><strong>{created_at[:10] if created_at else '정보 없음'}</strong></span>
          </div>
        </div>
        """
    hero_status_html = f"""
        <div class="folio-detail-action-meta">
            <span class="folio-detail-action-chip" aria-label="조회수 {view_count}">조회 {view_count:,}</span>
            <span class="folio-detail-action-chip {'is-private' if not is_public else 'is-public'}">{visibility_label}</span>
        </div>
        """

    def _render_hero_footer_actions() -> None:
        if like_error:
            st.error(like_error)
        meta_col, controls_col = st.columns(
            [4.4, 3.6],
            gap="medium",
            vertical_alignment="center",
        )

        with meta_col:
            st.markdown(hero_meta_html, unsafe_allow_html=True)

        with controls_col:
            with st.container(border=False, key="detail_footer_controls"):
                status_col, share_col, like_col = st.columns(
                    [1.0, 0.82, 0.72],
                    gap="small",
                    vertical_alignment="center",
                )

                with status_col:
                    st.markdown(hero_status_html, unsafe_allow_html=True)

                with share_col:
                    _render_share_button(project_id)

                with like_col:
                    _render_detail_like_button(project_id, like_count, user)

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
    has_visual_panel = bool(power_bi_url or project.get("power_bi_url") or has_report or has_github)

    if has_visual_panel:
        _render_project_visual_panel(project, power_bi_url, has_report, has_github)

    section_bodies = [
        project.get("problem"),
        project.get("dataset"),
        project.get("process"),
        project.get("insights"),
    ]
    if not any(section_bodies):
        st.info("아직 작성된 프로젝트 설명이 없습니다.")
    else:
        _render_sections(section_bodies)

    if st.button("← 홈 갤러리로 돌아가기", key="detail_content_back_button"):
        navigate(_HOME_PAGE)


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
                            aspect-ratio: 16 / 9;
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
                height=520,
            )
            st.caption("화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.")
        elif project.get("power_bi_url"):
            st.warning("Power BI 임베드 주소를 확인하세요. iframe 코드 또는 https URL의 src 값이 필요합니다.")

        actions = []
        if power_bi_url:
            actions.append(("대시보드 열기 ↗", power_bi_url))
        if has_report:
            actions.append(("보고서 보기 ↗", project["report_url"]))
        if has_github:
            actions.append(("GitHub 보기 ↗", project["github_url"]))
        if actions:
            action_cols = st.columns(len(actions), gap="medium")
            for action_col, (label, url) in zip(action_cols, actions):
                with action_col:
                    st.link_button(label, url, use_container_width=True)


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


def _render_share_button(project_id: str) -> None:
    components.html(
        _share_button_html(project_id),
        height=36,
    )


def _share_button_html(project_id: str) -> str:
    project_id_json = json.dumps(project_id)
    return f"""
    <style>
        html,
        body {{
            align-items: center;
            background: transparent;
            display: flex;
            height: 36px;
            justify-content: flex-end;
            margin: 0;
            overflow: hidden;
            padding: 0;
        }}
        .folio-share-button {{
            align-items: center;
            background: #ffffff;
            border: 1px solid #dce5f7;
            border-radius: 999px;
            color: #1459c8;
            cursor: pointer;
            display: inline-flex;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 12px;
            font-weight: 700;
            gap: 6px;
            height: 32px;
            justify-content: center;
            min-width: 96px;
            padding: 0 12px;
            transition: background 0.14s ease, border-color 0.14s ease, color 0.14s ease;
            width: auto;
        }}
        .folio-share-button:hover {{
            background: #eef3fd;
            border-color: rgba(20, 89, 200, 0.35);
        }}
        .folio-share-button svg {{
            height: 14px;
            width: 14px;
        }}
    </style>
    <button class="folio-share-button" type="button" id="folio-share-button" aria-label="공유 링크 복사">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M10 13a5 5 0 0 0 7.07 0l2.83-2.83a5 5 0 0 0-7.07-7.07L11.5 4.43"></path>
            <path d="M14 11a5 5 0 0 0-7.07 0L4.1 13.83a5 5 0 0 0 7.07 7.07l1.33-1.33"></path>
        </svg>
        <span id="folio-share-label">링크 복사</span>
    </button>
    <script>
        (function() {{
            var projectId = {project_id_json};
            var button = document.getElementById("folio-share-button");
            var label = document.getElementById("folio-share-label");
            function setLabel(text) {{
                label.textContent = text;
                window.setTimeout(function() {{ label.textContent = "링크 복사"; }}, 1600);
            }}
            function copyWithFallback(text) {{
                var input = document.createElement("textarea");
                input.value = text;
                input.setAttribute("readonly", "");
                input.style.position = "fixed";
                input.style.left = "-9999px";
                document.body.appendChild(input);
                input.select();
                var copied = document.execCommand("copy");
                document.body.removeChild(input);
                if (!copied) {{
                    throw new Error("copy failed");
                }}
            }}
            button.addEventListener("click", async function() {{
                var target = new URL(window.parent.location.origin + "/");
                target.searchParams.set("page", "Home");
                target.searchParams.set("project_id", projectId);
                target.searchParams.set("utm_source", "folio");
                target.searchParams.set("utm_medium", "share");
                target.searchParams.set("utm_campaign", "project_share");
                try {{
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        await navigator.clipboard.writeText(target.toString());
                    }} else {{
                        copyWithFallback(target.toString());
                    }}
                    setLabel("복사 완료");
                }} catch (error) {{
                    setLabel("복사 실패");
                }}
            }});
        }})();
    </script>
    """


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


def _render_sections(sections: list[str | None]) -> None:
    section_html = "".join(
        f'<section class="folio-detail-section">'
        f'<div class="folio-detail-section-content">{sanitize_project_html(body)}</div>'
        '</section>'
        for body in sections
        if body
    )
    st.markdown(
        clean_html(
            '<article class="folio-detail-content-card">'
            '<header class="folio-detail-content-heading"><h2>프로젝트 리포트</h2></header>'
            f'{section_html}</article>'
        ),
        unsafe_allow_html=True,
    )


def _clear_detail_query() -> None:
    navigate(_HOME_PAGE)
