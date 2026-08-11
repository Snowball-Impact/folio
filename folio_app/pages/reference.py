from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.assets import static_image_src
from folio_app.components.home_gallery import project_card_html, render_count_up_script
from folio_app.components.ui import clean_html
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
_VISIBLE_QUERY_PARAM = "visible"


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
    visible_count = _visible_reference_count(len(projects))
    _render_reference_grid(projects, platform_key, visible_count)
    _render_incremental_loader(platform_key, visible_count, len(projects))


def _selected_platform_key() -> str:
    platform_key = st.query_params.get("platform") or DEFAULT_REFERENCE_PLATFORM_KEY
    if platform_key not in REFERENCE_PLATFORM_BY_KEY:
        return DEFAULT_REFERENCE_PLATFORM_KEY
    return platform_key


def _visible_reference_count(total_count: int) -> int:
    try:
        current = int(st.query_params.get(_VISIBLE_QUERY_PARAM, _REFERENCE_PAGE_SIZE))
    except (TypeError, ValueError):
        current = _REFERENCE_PAGE_SIZE
    return min(max(current, _REFERENCE_PAGE_SIZE), total_count)


def _next_visible_count(current_count: int, total_count: int) -> int:
    return min(current_count + _REFERENCE_PAGE_SIZE, total_count)


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
                <h1 class="folio-reference-hero-title">
                    <span class="folio-reference-hero-count" data-folio-count-up="{project_count}">{project_count:,}</span><span class="folio-reference-hero-title-text">개의 공식 레퍼런스를 참고해보세요.</span>
                </h1>
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
        )
        for index, project in enumerate(projects[:visible_count])
    )
    st.markdown(
        f'<section class="folio-reference-grid" aria-label="레퍼런스 카드 목록">{cards_html}</section>',
        unsafe_allow_html=True,
    )


def _reference_card_slot_html(project: dict, platform_key: str, index: int) -> str:
    card_html = project_card_html(
        project,
        home_page=_REFERENCE_PAGE,
        extra_query_params=_reference_card_query_params(platform_key),
    )
    return (
        '<div class="folio-reference-card-slot" '
        f'data-folio-reference-card data-reference-index="{index}">{card_html}</div>'
    )


def _reference_card_query_params(platform_key: str) -> dict[str, str]:
    params = {"platform": platform_key}
    visible = st.query_params.get(_VISIBLE_QUERY_PARAM)
    if visible:
        params[_VISIBLE_QUERY_PARAM] = visible
    return params


def _render_incremental_loader(platform_key: str, visible_count: int, total_count: int) -> None:
    if visible_count >= total_count:
        st.markdown('<div class="folio-reference-end">모든 레퍼런스를 불러왔습니다.</div>', unsafe_allow_html=True)
        return

    remaining = total_count - visible_count
    st.markdown(
        f'<div class="folio-reference-loading-sentinel" data-visible="{visible_count}" data-total="{total_count}">'
        f'{remaining}개 더 볼 수 있습니다.</div>',
        unsafe_allow_html=True,
    )
    if st.button(
        f"{min(_REFERENCE_PAGE_SIZE, remaining)}개 더 보기",
        key=f"reference_load_more_{platform_key}",
        use_container_width=True,
    ):
        st.query_params[_VISIBLE_QUERY_PARAM] = str(_next_visible_count(visible_count, total_count))
        st.rerun()
    _render_auto_load_script(platform_key, visible_count, total_count)


def _render_auto_load_script(platform_key: str, visible_count: int, total_count: int) -> None:
    next_visible_count = _next_visible_count(visible_count, total_count)
    button_selector = f".st-key-reference_load_more_{platform_key} button"
    components.html(
        """
        <script>
        (function() {
            var parentWindow = window.parent;
            var parentDocument = parentWindow.document;
            var sentinelSelector = '.folio-reference-loading-sentinel';
            var buttonSelector = __BUTTON_SELECTOR__;
            var nextVisibleCount = __NEXT_VISIBLE_COUNT__;
            var boundAttribute = 'data-folio-reference-scroll-bound';
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

            function loadMore() {
                if (loading || !nearBottom()) {
                    return;
                }
                var button = parentDocument.querySelector(buttonSelector);
                if (!button) {
                    return;
                }
                loading = true;
                button.click();
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

                Array.from(parentDocument.querySelectorAll('section.stMain, [data-testid="stMain"], body *'))
                    .filter(function(element) {
                        if (element.getAttribute(boundAttribute) === 'true') {
                            return false;
                        }
                        var style = parentWindow.getComputedStyle(element);
                        var canScroll = /(auto|scroll|overlay)/.test(style.overflowY);
                        return canScroll && element.scrollHeight > element.clientHeight + 20;
                    })
                    .forEach(function(element) {
                        element.setAttribute(boundAttribute, 'true');
                        element.addEventListener("scroll", onScroll, { passive: true });
                        element.addEventListener("wheel", onScroll, { passive: true });
                        element.addEventListener("touchmove", onScroll, { passive: true });
                    });
            }

            bindScrollTargets();
            parentWindow.setTimeout(bindScrollTargets, 500);
            parentWindow.setTimeout(bindScrollTargets, 1500);
            parentWindow.setTimeout(loadMore, 300);
            parentWindow.setTimeout(loadMore, 900);
        })();
        </script>
        """
        .replace("__BUTTON_SELECTOR__", json.dumps(button_selector))
        .replace("__NEXT_VISIBLE_COUNT__", str(next_visible_count)),
        height=0,
    )
