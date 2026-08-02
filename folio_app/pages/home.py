import html

import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.assets import static_image_src
from folio_app.components.home_gallery import render_count_up_script, render_project_rails
from folio_app.components.ui import clean_html
from folio_app.navigation import navigate
from folio_app.pages import project_detail
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    list_popular_tags,
    list_public_projects,
)

_HOME_PAGE = "Home"
_HOME_HERO_SLIDES = (
    {
        "eyebrow": "Project Portfolio Platform",
        "title_html": "AI 시대에는 <em>휴먼 인사이트</em>가 자산이다.",
        "body": "데이터, AI, 웹 앱 프로젝트를 기록하고 공유하세요.",
        "visual": "preview",
    },
    {
        "eyebrow": "Collective Insight",
        "title_html": "인사이트는 <em>공유할수록 깊어집니다.</em>",
        "body": "프로젝트를 공유하고, 댓글과 반응으로 더 나은 결과물로 발전시키세요.",
        "visual": "guide",
    },
)
_HOME_GUIDE_STEPS = (
    ("01", "공유", "결과물과 제작 맥락을 모두와 공유합니다."),
    ("02", "피드백", "댓글과 반응으로 새로운 관점을 발견합니다."),
    ("03", "발전", "다양한 관점이 모여 인사이트를 개선합니다."),
)


def render() -> None:
    project_id = st.query_params.get("project_id")
    if project_id:
        project_detail.render(project_id)
        return

    _render_hero()
    search = st.query_params.get("q", "")
    selected_tag = st.query_params.get("tag", "전체")
    try:
        recent_projects = list_public_projects(search=search, tag=selected_tag, sort="최신순", limit=500)
        viewed_projects = list_public_projects(search=search, tag=selected_tag, sort="조회수순", limit=500)
        liked_projects = list_public_projects(search=search, tag=selected_tag, sort="좋아요순", limit=500)
        total_project_count = (
            len(recent_projects)
            if not search and selected_tag == "전체"
            else len(list_public_projects(sort="최신순", limit=500))
        )
        popular_tags = list_popular_tags()
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("다시 시도", key="retry_public_projects"):
            clear_project_caches()
            st.rerun()
        return
    _render_browse_panel(total_project_count, popular_tags)
    render_project_rails(_project_rail_specs(recent_projects, viewed_projects, liked_projects), home_page=_HOME_PAGE)


def _project_rail_specs(
    recent_projects: list[dict],
    viewed_projects: list[dict],
    liked_projects: list[dict],
) -> list[tuple[str, str, list[dict]]]:
    return [
        ("recent", "새로 공개된 프로젝트를 먼저 살펴보세요.", recent_projects),
        ("views", "많이 읽힌 프로젝트를 빠르게 훑어보세요.", viewed_projects),
        ("likes", "좋아요를 많이 받은 프로젝트를 확인해보세요.", liked_projects),
    ]


def _render_hero() -> None:
    slides_html = "".join(_hero_slide_html(slide) for slide in _HOME_HERO_SLIDES)
    st.markdown(
        clean_html(f"""
        <section class="folio-home-hero-shell">
            <div class="folio-home-hero-viewport">
                <div class="folio-home-hero-track">
                    {slides_html}
                </div>
            </div>
            <div class="folio-home-hero-dots" aria-hidden="true">
                <span></span>
                <span></span>
            </div>
        </section>
        """),
        unsafe_allow_html=True,
    )


def _render_browse_panel(project_count: int, popular_tags: list[str]) -> None:
    initial_search = st.query_params.get("q", "")
    initial_tag = st.query_params.get("tag", "전체")
    project_count_label = f"{project_count:,}"

    with st.container(border=False, key="folio_browse_panel"), st.form("browse_filters"):
        st.markdown(
            f"""
            <div class="folio-search-container">
                <div class="folio-search-heading">
                    <h1 class="folio-search-title">
                        <span class="folio-search-title-count" data-folio-count-up="{project_count}">{project_count_label}</span>개의
                        휴먼 인사이트 프로젝트가 FOLIO에 쌓이고 있어요.
                    </h1>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_count_up_script()

        search_col, submit_col = st.columns([5, 1])
        with search_col:
            search_input = st.text_input(
                "프로젝트 검색",
                value=initial_search,
                placeholder="프로젝트명, 태그, 작성자, 소속, 등록일로 검색",
                label_visibility="collapsed",
                key="browse_search",
            )
        with submit_col:
            submitted = st.form_submit_button("검색", type="primary", use_container_width=True)

        tag_options = ["전체", *popular_tags]
        if initial_tag not in tag_options:
            initial_tag = "전체"
        tag_col, tag_label_col = st.columns([5, 1.1], gap="small", vertical_alignment="center")
        with tag_col:
            selected_tag = st.pills(
                "태그 필터",
                tag_options,
                default=initial_tag,
                label_visibility="collapsed",
            ) or "전체"
        with tag_label_col:
            st.markdown('<div class="folio-popular-tag-label">인기 태그 TOP10</div>', unsafe_allow_html=True)

        if submitted:
            if search_input.strip():
                track_event("search", {"search_term": search_input.strip()})
            navigate(
                _HOME_PAGE,
                q=search_input.strip(),
                tag=selected_tag if selected_tag != "전체" else None,
            )


def _hero_slide_html(slide: dict[str, str]) -> str:
    hero_class = "folio-home-hero"
    if slide["visual"] == "guide":
        hero_class += " folio-home-guide-hero"
    return clean_html(f"""
    <section class="{hero_class}">
        <div class="folio-home-copy">
            <div class="folio-home-eyebrow">{html.escape(slide["eyebrow"])}</div>
            <h1>{slide["title_html"]}</h1>
            <p>{html.escape(slide["body"])}</p>
            <div class="folio-home-actions">
                <a class="folio-home-primary-cta" href="?page=Submit" target="_self">내 프로젝트 등록하기</a>
            </div>
        </div>
        {_hero_visual_html(slide["visual"])}
    </section>
    """)


def _hero_visual_html(visual: str) -> str:
    if visual == "preview":
        hero_preview_src = static_image_src("hero-preview-home.jpg")
        return (
            '<div class="folio-hero-preview">'
            f'<img class="folio-hero-preview-image" src="{hero_preview_src}" '
            'alt="데이터 분석 대시보드와 인사이트 미리보기" />'
            "</div>"
        )
    if visual == "guide":
        steps_html = "".join(_hero_guide_step_html(*step) for step in _HOME_GUIDE_STEPS)
        return f'<div class="folio-home-guide-flow" aria-label="프로젝트 발전 단계">{steps_html}</div>'
    return ""


def _hero_guide_step_html(step_number: str, title: str, body: str) -> str:
    return clean_html(f"""
    <div class="folio-home-guide-step">
        <div class="folio-home-guide-node">{html.escape(step_number)}</div>
        <div class="folio-home-guide-card">
            <strong>{html.escape(title)}</strong>
            <p>{html.escape(body)}</p>
        </div>
    </div>
    """)

