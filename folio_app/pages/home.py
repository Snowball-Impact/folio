import base64
import html
from functools import lru_cache
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.analytics import track_event
from folio_app.components.ui import plain_text, render_project_card_html
from folio_app.navigation import navigate
from folio_app.pages import project_detail
from folio_app.services.auth import get_current_user
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    list_popular_tags,
    list_public_projects,
)

_HERO_PREVIEW_PATH = Path(__file__).resolve().parent.parent / "static" / "hero-preview.png"
_HOME_PAGE = "Home"


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
    _render_project_rails(
        [
            ("recent", "최근 등록순", "새로 공개된 프로젝트를 먼저 살펴보세요.", recent_projects),
            ("views", "조회순", "많이 읽힌 프로젝트를 빠르게 훑어보세요.", viewed_projects),
            ("likes", "좋아요순", "좋아요를 많이 받은 프로젝트를 확인해보세요.", liked_projects),
        ]
    )


def _render_hero() -> None:
    hero_preview_src = _hero_preview_src()
    primary_href = "?page=Submit" if get_current_user() is not None else "?page=Login"
    st.markdown(
        f"""
        <section class="folio-home-hero-shell">
            <div class="folio-home-hero-viewport">
                <div class="folio-home-hero-track">
                    <section class="folio-home-hero">
                        <div class="folio-home-copy">
                            <div class="folio-home-eyebrow">Project Portfolio Platform</div>
                            <h1>AI 시대에는 <em>휴먼 인사이트</em>가 자산이다.</h1>
                            <p>데이터, AI, 웹 앱 프로젝트를 기록하고 공유하세요.</p>
                            <div class="folio-home-actions">
                                <a class="folio-home-primary-cta" href="{primary_href}">내 프로젝트 등록하기</a>
                            </div>
                        </div>
                        <div class="folio-hero-preview">
                            <img
                                class="folio-hero-preview-image"
                                src="{hero_preview_src}"
                                alt="데이터 분석 대시보드와 인사이트 미리보기"
                            />
                        </div>
                    </section>
                    <section class="folio-home-hero folio-home-guide-hero">
                        <div class="folio-home-copy">
                            <div class="folio-home-eyebrow">Collective Insight</div>
                            <h1>인사이트는 <em>공유할수록 깊어집니다.</em></h1>
                            <p>프로젝트를 공유하고, 댓글과 반응으로 더 나은 결과물로 발전시키세요.</p>
                            <div class="folio-home-actions">
                                <a class="folio-home-primary-cta" href="{primary_href}">내 프로젝트 등록하기</a>
                            </div>
                        </div>
                        <div class="folio-home-guide-flow" aria-label="프로젝트 발전 단계">
                            <div class="folio-home-guide-step">
                                <div class="folio-home-guide-node">01</div>
                                <div class="folio-home-guide-card">
                                    <strong>공유</strong>
                                    <p>결과물과 제작 맥락을 모두와 공유합니다.</p>
                                </div>
                            </div>
                            <div class="folio-home-guide-step">
                                <div class="folio-home-guide-node">02</div>
                                <div class="folio-home-guide-card">
                                    <strong>피드백</strong>
                                    <p>댓글과 반응으로 새로운 관점을 발견합니다.</p>
                                </div>
                            </div>
                            <div class="folio-home-guide-step">
                                <div class="folio-home-guide-node">03</div>
                                <div class="folio-home-guide-card">
                                    <strong>발전</strong>
                                    <p>다양한 관점이 모여 인사이트를 개선합니다.</p>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
            <div class="folio-home-hero-dots" aria-hidden="true">
                <span></span>
                <span></span>
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
            f"""
            <div class="folio-search-container">
                <div class="folio-search-heading">
                    <h1 class="folio-search-title">
                        <span class="folio-search-title-count" data-folio-count-up="{project_count}">0</span>개의
                        데이터·AI·웹 앱 프로젝트가 FOLIO에 쌓이고 있어요.
                    </h1>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _render_count_up_script()

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


def _render_project_rails(rails: list[tuple[str, str, str, list[dict]]]) -> None:
    if not any(projects for _, _, _, projects in rails):
        _render_rail_scroll_script()
        st.info("아직 표시할 프로젝트가 없습니다. 첫 프로젝트를 등록해보세요.")
        return

    for rail_key, title, description, projects in rails:
        _render_project_rail(rail_key, title, description, projects)
    _render_rail_scroll_script()


def _render_project_rail(rail_key: str, title: str, description: str, projects: list[dict]) -> None:
    cards_html = "".join(_project_card_html(project) for project in projects)
    safe_rail_key = html.escape(rail_key, quote=True)
    safe_description = html.escape(description)

    st.markdown(
        f"""
        <section class="folio-gallery-rail-section">
            <div class="folio-gallery-rail-head">
                <button
                    class="folio-rail-scroll-button"
                    type="button"
                    aria-label="{safe_description} 왼쪽으로 스크롤"
                    data-folio-rail-button
                    data-target="{safe_rail_key}"
                    data-direction="-1"
                >‹</button>
                <h3>{safe_description}</h3>
                <button
                    class="folio-rail-scroll-button"
                    type="button"
                    aria-label="{safe_description} 오른쪽으로 스크롤"
                    data-folio-rail-button
                    data-target="{safe_rail_key}"
                    data-direction="1"
                >›</button>
            </div>
        </section>
        <div class="folio-gallery-rail" data-folio-rail="{safe_rail_key}">
            {cards_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_rail_scroll_script() -> None:
    components.html(
        """
        <script>
        (function() {
            var parentDocument = window.parent.document;
            if (parentDocument.__folioRailScrollBound) {
                return;
            }
            parentDocument.__folioRailScrollBound = true;
            parentDocument.addEventListener("click", function(event) {
                var button = event.target.closest("[data-folio-rail-button]");
                if (!button) {
                    return;
                }
                event.preventDefault();
                var target = button.getAttribute("data-target");
                var direction = Number(button.getAttribute("data-direction") || "1");
                var rail = parentDocument.querySelector('[data-folio-rail="' + target + '"]');
                if (!rail) {
                    return;
                }
                var distance = Math.max(rail.clientWidth * 0.72, 320);
                rail.scrollBy({ left: direction * distance, behavior: "smooth" });
            });
        })();
        </script>
        """,
        height=0,
    )


def _render_count_up_script() -> None:
    components.html(
        """
        <script>
        (function() {
            var parentDocument = window.parent.document;
            var counters = parentDocument.querySelectorAll("[data-folio-count-up]");
            counters.forEach(function(counter) {
                var target = Number(counter.getAttribute("data-folio-count-up") || "0");
                var key = "folioCountAnimated:" + target;
                var duration = 720;
                var startTime = null;

                if (counter.dataset.folioAnimated === key) {
                    counter.textContent = target.toLocaleString("ko-KR");
                    return;
                }

                counter.dataset.folioAnimated = key;
                function tick(timestamp) {
                    if (startTime === null) {
                        startTime = timestamp;
                    }
                    var progress = Math.min((timestamp - startTime) / duration, 1);
                    var eased = 1 - Math.pow(1 - progress, 3);
                    var value = Math.round(target * eased);
                    counter.textContent = value.toLocaleString("ko-KR");
                    if (progress < 1) {
                        parentDocument.defaultView.requestAnimationFrame(tick);
                    }
                }
                parentDocument.defaultView.requestAnimationFrame(tick);
            });
        })();
        </script>
        """,
        height=0,
    )


def _project_card_html(project: dict) -> str:
    html_content = render_project_card_html(
        project,
        compact=False,
        fallback_text=plain_text(project.get("insights")) or "",
        href=f"?page={_HOME_PAGE}&project_id={project['id']}",
    )
    return html_content
