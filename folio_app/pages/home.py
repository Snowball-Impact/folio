import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

from folio_app.components.ui import plain_text, render_project_card_html
from folio_app.navigation import navigate
from folio_app.pages import project_detail
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    list_popular_tags,
    list_public_projects,
)

_HERO_PREVIEW_PATH = Path(__file__).resolve().parent.parent / "static" / "hero-preview.png"
_HOME_PAGE = "Home"
_GRID_COLUMNS = 3


@lru_cache(maxsize=1)
def _hero_preview_src() -> str:
    encoded = base64.b64encode(_HERO_PREVIEW_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render() -> None:
    project_id = st.query_params.get("project_id")
    if project_id:
        project_detail.render(project_id)
        return

    _render_hero()
    search = st.query_params.get("q", "")
    selected_tag = st.query_params.get("tag", "전체")
    sort = st.query_params.get("sort", "최신순")
    try:
        projects = list_public_projects(search=search, tag=selected_tag, sort=sort)
        popular_tags = list_popular_tags()
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("다시 시도", key="retry_public_projects"):
            clear_project_caches()
            st.rerun()
        return
    _render_browse_panel(len(projects), popular_tags)
    _render_project_grid(projects)


def _render_hero() -> None:
    hero_preview_src = _hero_preview_src()
    st.markdown(
        f"""
        <section class="folio-home-hero">
            <div class="folio-home-copy">
                <div class="folio-home-eyebrow">Data Portfolio Platform</div>
                <h1>AI 시대에는<br><em>휴먼 인사이트</em>가 자산이다.</h1>
                <p>발표로 끝나지 않는 프로젝트.<br>데이터 분석 결과를 커리어 자산으로 만드세요.</p>
            </div>
            <div class="folio-hero-preview">
                <img
                    class="folio-hero-preview-image"
                    src="{hero_preview_src}"
                    alt="데이터 분석 대시보드와 인사이트 미리보기"
                />
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_browse_panel(project_count: int, popular_tags: list[str]) -> None:
    initial_search = st.query_params.get("q", "")
    initial_tag = st.query_params.get("tag", "전체")

    with st.container(border=False, key="folio_browse_panel"), st.form("browse_filters"):
        st.markdown(
            """
            <div class="folio-search-container">
                <div class="folio-search-heading">
                    <div class="folio-search-title">프로젝트 탐색</div>
                    <div class="folio-search-subtitle">검색과 태그로 데이터 분석 포트폴리오를 찾아보세요.</div>
                </div>
                <div class="folio-search-count">총 {project_count}개</div>
            </div>
            """.format(project_count=project_count),
            unsafe_allow_html=True,
        )

        search_col, submit_col = st.columns([5, 1])
        with search_col:
            search_input = st.text_input(
                "프로젝트 검색",
                value=initial_search,
                placeholder="프로젝트명, 태그, 인사이트로 검색",
                label_visibility="collapsed",
                key="browse_search",
            )
        with submit_col:
            submitted = st.form_submit_button("검색", type="primary", use_container_width=True)

        filter_left, filter_right, reset_col = st.columns([4, 1.2, 1])
        with filter_left:
            tag_options = ["전체", *popular_tags]
            if initial_tag not in tag_options:
                initial_tag = "전체"
            selected_tag = st.pills(
                "태그 필터",
                tag_options,
                default=initial_tag,
            ) or "전체"
        with filter_right:
            sort_options = ["최신순", "조회수순", "좋아요순"]
            initial_sort = st.query_params.get("sort", "최신순")
            if initial_sort not in sort_options:
                initial_sort = "최신순"
            sort = st.selectbox("정렬", sort_options, index=sort_options.index(initial_sort))
        with reset_col:
            reset = st.form_submit_button("필터 초기화", use_container_width=True)

        if reset:
            st.session_state.pop("browse_search", None)
            navigate(_HOME_PAGE)
        if submitted:
            navigate(
                _HOME_PAGE,
                q=search_input.strip(),
                tag=selected_tag if selected_tag != "전체" else None,
                sort=sort if sort != "최신순" else None,
            )


def _render_project_grid(projects: list[dict]) -> None:
    if not projects:
        st.info("아직 표시할 프로젝트가 없습니다. 첫 프로젝트를 등록해보세요.")
        return

    for index in range(0, len(projects), _GRID_COLUMNS):
        cols = st.columns(_GRID_COLUMNS, gap="medium")
        for col, project in zip(cols, projects[index : index + _GRID_COLUMNS]):
            with col:
                _render_project_card(project)


def _render_project_card(project: dict) -> None:
    html_content = render_project_card_html(
        project,
        compact=False,
        fallback_text=plain_text(project.get("insights")) or "",
        href=f"?page={_HOME_PAGE}&project_id={project['id']}",
    )
    st.markdown(html_content, unsafe_allow_html=True)
