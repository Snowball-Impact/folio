from __future__ import annotations

import html
import re
from urllib.parse import urlparse

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.layout import render_hero
from folio_app.components.ui import render_gallery_card_html, render_tag_chips
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
        selected_tag = st.pills(
            "자주 사용되는 태그",
            ["전체", *popular_tags],
            default="전체",
        ) or "전체"
    with right:
        sort = st.selectbox("정렬", ["최신순", "조회수순", "좋아요순"])

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
    body = render_gallery_card_html(project)
    st.markdown(body, unsafe_allow_html=True)
    if st.button("상세 보기", key=f"open_{project['id']}", use_container_width=True):
        st.query_params["page"] = "Gallery"
        st.query_params["project_id"] = project["id"]
        st.rerun()


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

    if st.button("← 갤러리로 돌아가기"):
        _clear_detail_query()
        st.rerun()

    author = project.get("author") or {}
    created_at = project.get("created_at") or ""
    category = project.get("category") or ""
    author_name = author.get("name") or "작성자"

    render_hero(
        "Project",
        project.get("title") or "Untitled",
        f"{author_name} · {created_at[:10] if created_at else '등록일 없음'}",
    )

    like_state_key = f"liked_{project_id}"
    liked = st.session_state.get(like_state_key, False)
    like_count = project.get("like_count", 0) or 0
    if liked:
        like_count += 1

    st.markdown(
        f"""
        <div class="folio-detail-header">
            <div class="folio-detail-meta">
                <span>{html.escape(category)}</span>
                <span>조회 {project.get("view_count", 0)}</span>
                <span>좋아요 {like_count}</span>
            </div>
            {render_tag_chips(project.get("tags") or [])}
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        if _is_http_url(project.get("thumbnail_url")):
            st.image(project["thumbnail_url"], use_container_width=True)

        if st.button("좋아요" if not liked else "좋아요 취소", key=f"like_button_{project_id}", use_container_width=True):
            st.session_state[like_state_key] = not liked
            st.experimental_rerun()

        power_bi_url = normalize_power_bi_embed_url(project.get("power_bi_url"))
        if power_bi_url:
            st.markdown("### Power BI 대시보드")
            components.html(
                f"""
                <iframe
                    title="Power BI report"
                    width="100%"
                    height="420"
                    src="{html.escape(power_bi_url, quote=True)}"
                    frameborder="0"
                    allowFullScreen="true">
                </iframe>
                """,
                height=440,
            )
        elif project.get("power_bi_url"):
            st.warning("Power BI 임베드 주소를 확인하세요. iframe 코드 또는 https URL의 src 값이 필요합니다.")

        has_report = _is_http_url(project.get("report_url"))
        has_github = _is_http_url(project.get("github_url"))
        if has_report or has_github:
            st.markdown("### 첨부 파일 및 링크")
            if has_report:
                st.link_button("보고서 보기", project["report_url"], use_container_width=True)
            if has_github:
                st.link_button("GitHub 보기", project["github_url"], use_container_width=True)
        elif not power_bi_url and not _is_http_url(project.get("thumbnail_url")):
            st.info("등록된 대시보드나 외부 링크가 없습니다.")


def _render_section(title: str, body: str | None) -> None:
    if not body:
        return
    st.markdown(f"### {title}")
    st.markdown(body, unsafe_allow_html=True)


def _clear_detail_query() -> None:
    st.query_params.clear()
    st.query_params["page"] = "Gallery"
