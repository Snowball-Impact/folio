import html
import re
from urllib.parse import urlparse

import streamlit as st

from folio_app.components.ui import plain_text, render_project_card_html, render_tag_chips
from folio_app.services.projects import list_popular_tags, list_public_projects


def render() -> None:
    st.markdown(
        """
        <section class="folio-home-hero">
            <div class="folio-home-copy">
                <h1>발표로 끝나지 않는<br>프로젝트</h1>
                <p>데이터 분석 프로젝트를 포트폴리오 자산으로 축적하고 공유하는 플랫폼, FOLIO</p>
            </div>
            <div class="folio-hero-preview">
                <div class="folio-preview-window"></div>
                <div class="folio-preview-card">
                    <strong>프로젝트 인사이트</strong>
                    <span>사용자의 숨은 패턴을 발견했습니다.</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='folio-search-container'>
            <div class='folio-search-title'>검색</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    search_col, button_col = st.columns([5, 1], gap="small")
    with search_col:
        search = st.text_input(
            "",
            placeholder="프로젝트명, 태그, 인사이트로 검색",
            label_visibility="collapsed",
            key="home_search",
        )
    with button_col:
        if st.button("🔎", key="home_search_button", use_container_width=True):
            st.query_params["page"] = "Gallery"
            st.query_params["q"] = search or ""
            st.rerun()

    tags = list_popular_tags(limit=6)
    if tags:
        st.markdown(render_tag_chips(tags), unsafe_allow_html=True)

    popular_projects = list_public_projects(sort="조회수순", limit=4)
    if not popular_projects:
        st.info("아직 등록된 프로젝트가 없습니다.")
        return

    _render_project_section("인기 프로젝트", popular_projects, card_style="visual")


def _render_project_section(title: str, projects: list[dict], card_style: str) -> None:
    if not projects:
        return

    st.markdown(f"### {title}")
    cols = st.columns(4)
    for col, project in zip(cols, projects):
        with col:
            _render_home_card(project, compact=card_style == "compact")
            if st.button("보기", key=f"home_open_{card_style}_{project['id']}"):
                st.query_params["page"] = "Gallery"
                st.query_params["project_id"] = project["id"]
                st.rerun()


def _render_home_card(project: dict, compact: bool = False) -> None:
    html_content = render_project_card_html(
        project,
        compact=compact,
        fallback_text=plain_text(project.get("insights")) or "",
    )
    st.markdown(html_content, unsafe_allow_html=True)
