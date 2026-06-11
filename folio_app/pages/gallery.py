from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.layout import render_hero
from folio_app.components.ui import is_http_url, render_gallery_card_html, render_tag_chips
from folio_app.services.projects import (
    get_project,
    increment_view_count,
    list_popular_tags,
    list_public_projects,
    normalize_power_bi_embed_url,
)


def render() -> None:
    project_id = st.query_params.get("project_id")
    if project_id:
        _render_detail(project_id)
        return

    render_hero(
        "Gallery",
        "프로젝트 갤러리",
        "데이터 분석 포트폴리오와 인사이트를 탐색하세요.",
    )

    initial_search = st.query_params.get("q", "")
    search = st.text_input("검색어 입력", value=initial_search, placeholder="예: Power BI, 공공데이터, 취업")

    st.markdown('<div class="folio-filter-row"></div>', unsafe_allow_html=True)
    left, right = st.columns([2, 1])
    with left:
        popular_tags = list_popular_tags()
        tag_options = ["전체", *popular_tags]
        initial_tag = st.query_params.get("tag", "전체")
        if initial_tag not in tag_options:
            initial_tag = "전체"
        selected_tag = st.pills(
            "태그 필터",
            tag_options,
            default=initial_tag,
        ) or "전체"
    with right:
        sort = st.selectbox("정렬", ["최신순", "조회수순", "좋아요순"])

    if search or selected_tag != "전체":
        if st.button("검색/태그 필터 초기화", use_container_width=True):
            st.query_params.clear()
            st.query_params["page"] = "Gallery"
            st.rerun()

    projects = list_public_projects(
        search=search,
        tag=selected_tag,
        sort=sort,
    )
    if not projects:
        st.info("아직 표시할 프로젝트가 없습니다. 첫 프로젝트를 등록해보세요.")
        return

    st.markdown(f"**총 {len(projects)}개의 프로젝트**")
    for project in projects:
        _render_project_card(project)


def _render_project_card(project: dict) -> None:
    body = render_gallery_card_html(project, href=f"?page=Gallery&project_id={project['id']}")
    st.markdown(body, unsafe_allow_html=True)


def _render_detail(project_id: str) -> None:
    viewed_key = f"viewed_{project_id}"
    if not st.session_state.get(viewed_key):
        increment_view_count(project_id)
        st.session_state[viewed_key] = True

    project = get_project(project_id)
    if project is None:
        st.error("프로젝트를 찾을 수 없습니다.")
        if st.button("갤러리로 돌아가기"):
            _clear_detail_query()
            st.rerun()
        return

    author = project.get("author") or {}
    created_at = project.get("created_at") or ""
    author_name = author.get("name") or "작성자"

    like_count = project.get("like_count", 0) or 0

    st.markdown(
        f"""
        <section class="folio-hero folio-detail-hero">
            <div>
                <h1>{html.escape(project.get("title") or "Untitled")}</h1>
                <p class="folio-muted">{html.escape(author_name)} · {created_at[:10] if created_at else '등록일 없음'}</p>
            </div>
            <div class="folio-detail-hero-meta">
                {render_tag_chips(project.get("tags") or [])}
                <div class="folio-detail-meta">
                    <span>조회 {project.get("view_count", 0)}</span>
                    <span>좋아요 {like_count}</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    has_report = is_http_url(project.get("report_url"))
    has_github = is_http_url(project.get("github_url"))
    power_bi_url = normalize_power_bi_embed_url(project.get("power_bi_url"))

    content_col, side_col = st.columns([1.75, 1])
    with content_col:
        if project.get("ai_summary"):
            st.markdown("### AI 요약")
            st.info(project["ai_summary"])

        _render_section("문제 정의", project.get("problem"))
        _render_section("사용 데이터", project.get("dataset"))
        _render_section("분석 과정", project.get("process"))
        _render_section("핵심 인사이트", project.get("insights"))

    with side_col:
        if power_bi_url:
            st.markdown("### 대시보드")
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
                    .folio-dashboard-iframe {{
                        border: 0;
                        height: 100%;
                        inset: 0;
                        position: absolute;
                        width: 100%;
                    }}
                </style>
                <div class="folio-dashboard-frame">
                    <iframe
                        title="Embedded dashboard"
                        src="{html.escape(power_bi_url, quote=True)}"
                        frameborder="0"
                        allowFullScreen="true"
                        class="folio-dashboard-iframe">
                    </iframe>
                </div>
                """,
                height=340,
            )
        elif project.get("power_bi_url"):
            st.warning("Power BI 임베드 주소를 확인하세요. iframe 코드 또는 https URL의 src 값이 필요합니다.")

        if has_report or has_github:
            st.markdown('<div class="folio-attachment-links">', unsafe_allow_html=True)
            st.markdown("### 첨부 파일 및 링크")
            if has_report:
                st.link_button("보고서 보기", project["report_url"], use_container_width=True)
            if has_github:
                st.link_button("GitHub 보기", project["github_url"], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<a class="folio-back-link folio-back-link-bottom" href="?page=Gallery" target="_self">← 목록으로 돌아가기</a>',
        unsafe_allow_html=True,
    )


def _render_section(title: str, body: str | None) -> None:
    if not body:
        return
    st.markdown(f"### {title}")
    st.markdown(body, unsafe_allow_html=True)


def _clear_detail_query() -> None:
    st.query_params.clear()
    st.query_params["page"] = "Gallery"
