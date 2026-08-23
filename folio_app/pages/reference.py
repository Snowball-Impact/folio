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
    VISIBLE_REFERENCE_PLATFORMS,
    is_visible_reference_platform,
    reference_projects_for_platform,
)
from folio_app.services.projects import ProjectServiceError, clear_project_caches, list_public_projects


_REFERENCE_PAGE = "Reference"
_REFERENCE_PAGE_SIZE = 12
_VISIBLE_QUERY_PARAM = "visible"
_REFERENCE_SORT_OPTIONS = (
    ("latest", "최신", "최신순"),
    ("likes", "좋아요", "좋아요순"),
    ("views", "조회수", "조회수순"),
)
_DEFAULT_REFERENCE_SORT_KEY = "latest"


def render() -> None:
    project_id = st.query_params.get("project_id")
    if project_id:
        sort_key = _selected_sort_key()
        project_detail.render(
            project_id,
            back_page=_REFERENCE_PAGE,
            back_label="레퍼런스로 돌아가기",
            back_params=_reference_back_params(_selected_platform_key(), sort_key),
        )
        return

    platform_key = _selected_platform_key()
    sort_key = _selected_sort_key()
    try:
        projects = reference_projects_for_platform(
            list_public_projects(sort=_sort_label_for_query(sort_key), limit=500),
            platform_key,
        )
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("다시 시도", key="retry_reference_projects"):
            clear_project_caches()
            st.rerun()
        return

    _render_reference_hero(platform_key, len(projects))
    _render_reference_sort_bar(sort_key)
    visible_count = _visible_reference_count(len(projects))
    _render_reference_grid(projects, platform_key, sort_key, visible_count)
    _render_reference_sort_script(platform_key, sort_key, visible_count)
    _render_incremental_loader(platform_key, visible_count, len(projects))


def _selected_platform_key() -> str:
    platform_key = st.query_params.get("platform") or DEFAULT_REFERENCE_PLATFORM_KEY
    if platform_key not in REFERENCE_PLATFORM_BY_KEY or not is_visible_reference_platform(platform_key):
        return DEFAULT_REFERENCE_PLATFORM_KEY
    return platform_key


def _selected_sort_key() -> str:
    sort_key = st.query_params.get("sort") or _DEFAULT_REFERENCE_SORT_KEY
    if sort_key not in {key for key, _, _ in _REFERENCE_SORT_OPTIONS}:
        return _DEFAULT_REFERENCE_SORT_KEY
    return sort_key


def _sort_label_for_query(sort_key: str) -> str:
    return next(
        sort_query
        for key, _, sort_query in _REFERENCE_SORT_OPTIONS
        if key == sort_key
    )


def _reference_back_params(platform_key: str, sort_key: str) -> dict[str, str]:
    params = {"platform": platform_key}
    if sort_key != _DEFAULT_REFERENCE_SORT_KEY:
        params["sort"] = sort_key
    return params


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
    nav_html = "".join(_platform_nav_item_html(platform_item, platform_key) for platform_item in VISIBLE_REFERENCE_PLATFORMS)
    st.markdown(
        clean_html(f"""
        <section class="folio-reference-hero-shell">
            <div class="folio-reference-hero-copy">
                <div class="folio-page-hero-eyebrow">Reference Library</div>
                <h1 class="folio-reference-hero-title">
                    <span class="folio-reference-hero-count" data-folio-count-up="{project_count}">{project_count:,}</span><span class="folio-reference-hero-title-text">개의 레퍼런스를 참고해보세요.</span>
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
        "tableau": "reference-tableau-logo-cropped.webp",
        "powerbi": "reference-powerbi-logo-cropped.webp",
        "datastudio": "reference-datastudio-logo-cropped.webp",
        "streamlit": "reference-streamlit-logo-cropped.webp",
    }.get(platform_key)
    if not logo_file:
        return ""
    safe_platform_key = html.escape(platform_key)
    logo_src = static_image_src(logo_file)
    return (
        f'<img class="folio-reference-logo-image folio-reference-logo-image-{safe_platform_key}" '
        f'src="{logo_src}" alt="" />'
    )


def _render_reference_sort_bar(sort_key: str) -> None:
    sort_items_html = "".join(
        _sort_item_html(sort_key, key, label)
        for key, label, _ in _REFERENCE_SORT_OPTIONS
    )
    st.markdown(
        clean_html(f"""
        <div class="folio-reference-sort-bar" aria-label="레퍼런스 정렬">
            <span>정렬</span>
            <nav class="folio-reference-sort-tabs">
                {sort_items_html}
            </nav>
        </div>
        """),
        unsafe_allow_html=True,
    )


def _sort_item_html(selected_sort_key: str, sort_key: str, label: str) -> str:
    active_class = " is-active" if sort_key == selected_sort_key else ""
    return (
        f'<button class="folio-reference-sort-tab{active_class}" '
        f'type="button" data-folio-reference-sort="{html.escape(sort_key, quote=True)}">'
        f'{html.escape(label)}</button>'
    )


def _render_reference_grid(projects: list[dict], platform_key: str, sort_key: str, visible_count: int) -> None:
    if not projects:
        st.info("아직 표시할 레퍼런스가 없습니다.")
        return

    cards_html = "".join(
        _reference_card_slot_html(
            project,
            platform_key,
            sort_key,
            visible_count,
            index,
        )
        for index, project in enumerate(projects)
    )
    st.markdown(
        f'<section class="folio-reference-grid" aria-label="레퍼런스 카드 목록" '
        f'data-folio-reference-grid data-visible-count="{visible_count}">{cards_html}</section>',
        unsafe_allow_html=True,
    )


def _reference_card_slot_html(
    project: dict,
    platform_key: str,
    sort_key: str,
    visible_count: int,
    index: int,
) -> str:
    card_html = project_card_html(
        project,
        home_page=_REFERENCE_PAGE,
        extra_query_params=_reference_card_query_params(platform_key, sort_key),
    )
    hidden_class = " is-hidden" if index >= visible_count else ""
    safe_created_at = html.escape(str(project.get("created_at") or ""), quote=True)
    like_count = int(project.get("like_count") or 0)
    view_count = int(project.get("view_count") or 0)
    project_id = html.escape(str(project.get("id") or ""), quote=True)
    return (
        f'<div class="folio-reference-card-slot{hidden_class}" '
        f'data-folio-reference-card data-reference-index="{index}" data-project-id="{project_id}" '
        f'data-created-at="{safe_created_at}" data-like-count="{like_count}" data-view-count="{view_count}">'
        f'{card_html}</div>'
    )


def _reference_card_query_params(platform_key: str, sort_key: str) -> dict[str, str]:
    params = {"platform": platform_key}
    if sort_key != _DEFAULT_REFERENCE_SORT_KEY:
        params["sort"] = sort_key
    visible = st.query_params.get(_VISIBLE_QUERY_PARAM)
    if visible:
        params[_VISIBLE_QUERY_PARAM] = visible
    return params


def _render_reference_sort_script(platform_key: str, sort_key: str, visible_count: int) -> None:
    components.html(
        """
        <script>
        (function() {
            var parentWindow = window.parent;
            var parentDocument = parentWindow.document;
            var gridSelector = "[data-folio-reference-grid]";
            var sortButtonSelector = "[data-folio-reference-sort]";
            var selectedSort = __SORT_KEY__;
            var platformKey = __PLATFORM_KEY__;
            var visibleCount = __VISIBLE_COUNT__;

            function numericValue(card, attributeName) {
                return Number(card.getAttribute(attributeName) || "0") || 0;
            }

            function createdValue(card) {
                return Date.parse(card.getAttribute("data-created-at") || "") || 0;
            }

            function compareCards(sortKey, first, second) {
                if (sortKey === "likes") {
                    return numericValue(second, "data-like-count") - numericValue(first, "data-like-count")
                        || createdValue(second) - createdValue(first);
                }
                if (sortKey === "views") {
                    return numericValue(second, "data-view-count") - numericValue(first, "data-view-count")
                        || createdValue(second) - createdValue(first);
                }
                return createdValue(second) - createdValue(first);
            }

            function updateDetailLinks(sortKey) {
                var currentUrl = new URL(parentWindow.location.href);
                var visible = currentUrl.searchParams.get("visible");
                parentDocument.querySelectorAll("[data-folio-reference-card] a[href]").forEach(function(anchor) {
                    var href = new URL(anchor.getAttribute("href"), parentWindow.location.href);
                    href.searchParams.set("page", "Reference");
                    href.searchParams.set("platform", platformKey);
                    if (sortKey === "latest") {
                        href.searchParams.delete("sort");
                    } else {
                        href.searchParams.set("sort", sortKey);
                    }
                    if (visible) {
                        href.searchParams.set("visible", visible);
                    } else {
                        href.searchParams.delete("visible");
                    }
                    anchor.setAttribute("href", "?" + href.searchParams.toString());
                });
            }

            function updateUrl(sortKey) {
                var url = new URL(parentWindow.location.href);
                url.searchParams.set("page", "Reference");
                url.searchParams.set("platform", platformKey);
                if (sortKey === "latest") {
                    url.searchParams.delete("sort");
                } else {
                    url.searchParams.set("sort", sortKey);
                }
                parentWindow.history.pushState({}, "", url);
            }

            function updateButtons(sortKey) {
                parentDocument.querySelectorAll(sortButtonSelector).forEach(function(button) {
                    button.classList.toggle("is-active", button.getAttribute("data-folio-reference-sort") === sortKey);
                });
            }

            function applySort(sortKey, shouldPushUrl) {
                var grid = parentDocument.querySelector(gridSelector);
                if (!grid) {
                    return;
                }
                var cards = Array.from(grid.querySelectorAll("[data-folio-reference-card]"));
                cards.sort(function(first, second) {
                    return compareCards(sortKey, first, second);
                });
                cards.forEach(function(card, index) {
                    card.classList.toggle("is-hidden", index >= visibleCount);
                    grid.appendChild(card);
                });
                updateButtons(sortKey);
                updateDetailLinks(sortKey);
                if (shouldPushUrl) {
                    updateUrl(sortKey);
                }
            }

            parentWindow.__folioReferenceSortState = { applySort: applySort };

            if (!parentDocument.__folioReferenceSortBound) {
                parentDocument.__folioReferenceSortBound = true;
                parentDocument.addEventListener("click", function(event) {
                    var button = event.target.closest(sortButtonSelector);
                    if (!button) {
                        return;
                    }
                    event.preventDefault();
                    var state = parentWindow.__folioReferenceSortState;
                    if (state && typeof state.applySort === "function") {
                        state.applySort(button.getAttribute("data-folio-reference-sort") || "latest", true);
                    }
                });
            }

            parentWindow.setTimeout(function() {
                applySort(selectedSort, false);
            }, 0);
        })();
        </script>
        """
        .replace("__SORT_KEY__", json.dumps(sort_key))
        .replace("__PLATFORM_KEY__", json.dumps(platform_key))
        .replace("__VISIBLE_COUNT__", str(visible_count)),
        height=0,
    )


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
