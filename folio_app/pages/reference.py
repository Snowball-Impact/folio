from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.assets import static_image_src
from folio_app.components.home_gallery import project_card_html, render_card_preview_script, render_count_up_script
from folio_app.components.ui import clean_html
from folio_app.navigation import navigate
from folio_app.pages import project_detail
from folio_app.services.project_references import (
    DEFAULT_REFERENCE_PLATFORM_KEY,
    REFERENCE_PLATFORM_BY_KEY,
    REFERENCE_PLATFORMS,
    reference_projects_for_platform,
)
from folio_app.services.projects import ProjectServiceError, clear_project_caches, list_public_projects


_REFERENCE_PAGE = "Reference"
_REFERENCE_PAGE_SIZE = 12


def render() -> None:
    project_id = st.query_params.get("project_id")
    if project_id:
        project_detail.render(
            project_id,
            back_page=_REFERENCE_PAGE,
            back_label="레퍼런스로 돌아가기",
            back_params={"platform": _selected_platform_key()},
        )
        return

    platform_key = _selected_platform_key()
    platform = REFERENCE_PLATFORM_BY_KEY[platform_key]

    try:
        projects = reference_projects_for_platform(
            list_public_projects(sort="최신순", limit=500),
            platform_key,
        )
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("다시 시도", key="retry_reference_projects"):
            clear_project_caches()
            st.rerun()
        return

    _render_reference_hero(platform_key, len(projects))
    initial_visible_count = min(_REFERENCE_PAGE_SIZE, len(projects))
    _render_reference_grid(projects, platform_key, initial_visible_count)
    _render_incremental_loader(initial_visible_count, len(projects))


def _selected_platform_key() -> str:
    platform_key = st.query_params.get("platform") or DEFAULT_REFERENCE_PLATFORM_KEY
    if platform_key not in REFERENCE_PLATFORM_BY_KEY:
        return DEFAULT_REFERENCE_PLATFORM_KEY
    return platform_key


def _render_reference_hero(platform_key: str, project_count: int) -> None:
    platform = REFERENCE_PLATFORM_BY_KEY[platform_key]
    safe_label = html.escape(platform.label)
    safe_description = html.escape(platform.description)
    nav_html = "".join(_platform_nav_item_html(platform_item, platform_key) for platform_item in REFERENCE_PLATFORMS)
    st.markdown(
        clean_html(f"""
        <section class="folio-reference-hero-shell">
            <div class="folio-reference-hero-copy">
                <div class="folio-page-hero-eyebrow">Reference Library</div>
                <div class="folio-reference-hero-title" role="heading" aria-level="1">
                    <span data-folio-count-up="{project_count}">{project_count:,}</span>개의 공식 레퍼런스를 참고해보세요.
                </div>
                <p>{safe_description}</p>
            </div>
            <div class="folio-reference-hero-visual" aria-label="{safe_label}">
                <div class="folio-reference-hero-logo">
                    {_platform_logo_html(platform_key)}
                </div>
                <nav class="folio-reference-hero-tabs" aria-label="레퍼런스 플랫폼">
                    {nav_html}
                </nav>
            </div>
        </section>
        """),
        unsafe_allow_html=True,
    )
    render_count_up_script()


def _platform_nav_item_html(platform, selected_key: str) -> str:
    active_class = " is-active" if platform.key == selected_key else ""
    return (
        f'<a class="folio-reference-hero-tab{active_class}" '
        f'href="?page={_REFERENCE_PAGE}&platform={html.escape(platform.key, quote=True)}" target="_self">'
        f'{html.escape(platform.label)}</a>'
    )


def _platform_logo_html(platform_key: str) -> str:
    logo_file = {
        "tableau": "reference-tableau-logo-cropped.png",
        "powerbi": "reference-powerbi-logo-cropped.png",
        "datastudio": "reference-datastudio-logo-cropped.png",
        "streamlit": "reference-streamlit-logo-cropped.png",
    }.get(platform_key)
    if not logo_file:
        return ""
    safe_platform_key = html.escape(platform_key)
    logo_src = static_image_src(logo_file)
    return (
        f'<img class="folio-reference-logo-image folio-reference-logo-image-{safe_platform_key}" '
        f'src="{logo_src}" alt="" />'
    )


def _render_reference_grid(projects: list[dict], platform_key: str, visible_count: int) -> None:
    if not projects:
        st.info("아직 표시할 레퍼런스가 없습니다.")
        return

    cards_html = "".join(
        _reference_card_slot_html(
            project,
            platform_key,
            index,
            is_visible=index < visible_count,
        )
        for index, project in enumerate(projects)
    )
    st.markdown(
        f'<section class="folio-reference-grid" aria-label="레퍼런스 카드 목록">{cards_html}</section>',
        unsafe_allow_html=True,
    )
    render_card_preview_script()


def _reference_card_slot_html(project: dict, platform_key: str, index: int, *, is_visible: bool) -> str:
    hidden_class = "" if is_visible else " is-hidden"
    card_html = project_card_html(
        project,
        home_page=_REFERENCE_PAGE,
        extra_query_params={"platform": platform_key},
    )
    return (
        f'<div class="folio-reference-card-slot{hidden_class}" '
        f'data-folio-reference-card data-reference-index="{index}">{card_html}</div>'
    )


def _render_incremental_loader(visible_count: int, total_count: int) -> None:
    if visible_count >= total_count:
        st.markdown('<div class="folio-reference-end">모든 레퍼런스를 불러왔습니다.</div>', unsafe_allow_html=True)
        return

    remaining = total_count - visible_count
    st.markdown(
        f'<div class="folio-reference-loading-sentinel" data-visible="{visible_count}" data-total="{total_count}">'
        f'{remaining}개 더 볼 수 있습니다.</div>',
        unsafe_allow_html=True,
    )
    _render_auto_load_script()


def _render_auto_load_script() -> None:
    components.html(
        """
        <script>
        (function() {
            var parentWindow = window.parent;
            var parentDocument = parentWindow.document;
            var sentinelSelector = '.folio-reference-loading-sentinel';
            var cardSelector = '[data-folio-reference-card]';
            var boundAttribute = 'data-folio-reference-scroll-bound';
            var pageSize = 12;
            var ticking = false;
            var loading = false;

            function nearBottom() {
                var sentinel = parentDocument.querySelector(sentinelSelector);
                if (!sentinel) {
                    return false;
                }
                var rect = sentinel.getBoundingClientRect();
                var viewportHeight = parentWindow.innerHeight || parentDocument.documentElement.clientHeight;
                return rect.top < viewportHeight + 260;
            }

            function visibleCards() {
                return Array.from(parentDocument.querySelectorAll(cardSelector + ':not(.is-hidden)'));
            }

            function hiddenCards() {
                return Array.from(parentDocument.querySelectorAll(cardSelector + '.is-hidden'));
            }

            function updateSentinel() {
                var sentinel = parentDocument.querySelector(sentinelSelector);
                if (!sentinel) {
                    return;
                }
                var hidden = hiddenCards();
                if (!hidden.length) {
                    sentinel.className = 'folio-reference-end';
                    sentinel.textContent = '모든 레퍼런스를 불러왔습니다.';
                    return;
                }
                var visible = visibleCards().length;
                var total = visible + hidden.length;
                sentinel.dataset.visible = String(visible);
                sentinel.dataset.total = String(total);
                sentinel.textContent = hidden.length.toLocaleString('ko-KR') + '개 더 볼 수 있습니다.';
            }

            function loadMore() {
                if (loading || !nearBottom()) {
                    return;
                }
                var cards = hiddenCards();
                if (!cards.length) {
                    updateSentinel();
                    return;
                }
                loading = true;
                cards.slice(0, pageSize).forEach(function(card) {
                    card.classList.remove('is-hidden');
                });
                updateSentinel();
                parentWindow.setTimeout(function() {
                    loading = false;
                    if (nearBottom()) {
                        loadMore();
                    }
                }, 160);
            }

            function onScroll() {
                if (ticking) {
                    return;
                }
                ticking = true;
                parentWindow.requestAnimationFrame(function() {
                    ticking = false;
                    loadMore();
                });
            }

            function bindScrollTargets() {
                parentWindow.addEventListener("scroll", onScroll, { passive: true });
                parentWindow.addEventListener("wheel", onScroll, { passive: true });
                parentWindow.addEventListener("touchmove", onScroll, { passive: true });
                parentWindow.addEventListener("keydown", onScroll, { passive: true });
                parentDocument.addEventListener("scroll", onScroll, { passive: true, capture: true });

                Array.from(parentDocument.querySelectorAll("body, body *")).forEach(function(element) {
                    if (element.getAttribute(boundAttribute) === "1") {
                        return;
                    }
                    var style = parentWindow.getComputedStyle(element);
                    if (/(auto|scroll)/.test(style.overflowY) && element.scrollHeight > element.clientHeight) {
                        element.setAttribute(boundAttribute, "1");
                        element.addEventListener("scroll", onScroll, { passive: true });
                    }
                });
            }

            if ("IntersectionObserver" in parentWindow) {
                var observer = new parentWindow.IntersectionObserver(function(entries) {
                    entries.forEach(function(entry) {
                        if (entry.isIntersecting) {
                            loadMore();
                        }
                    });
                }, { root: null, rootMargin: "260px 0px" });
                var sentinel = parentDocument.querySelector(sentinelSelector);
                if (sentinel) {
                    observer.observe(sentinel);
                }
            }

            updateSentinel();
            bindScrollTargets();
            if ("MutationObserver" in parentWindow) {
                var mutationObserver = new parentWindow.MutationObserver(bindScrollTargets);
                mutationObserver.observe(parentDocument.body, { childList: true, subtree: true });
            }
            parentWindow.setTimeout(loadMore, 300);
            parentWindow.setTimeout(loadMore, 900);
            parentWindow.setTimeout(bindScrollTargets, 1200);
            parentWindow.setInterval(loadMore, 1200);
            parentWindow.setInterval(bindScrollTargets, 1800);
        })();
        </script>
        """,
        height=0,
    )
