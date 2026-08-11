"""Home gallery rail rendering helpers."""

from __future__ import annotations

import html
from urllib.parse import urlencode

import streamlit as st
import streamlit.components.v1 as components

from folio_app.components.ui import plain_text, render_project_card_html
from folio_app.services.projects import normalize_power_bi_embed_url


_RAIL_SCROLL_SCRIPT = """
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
        var firstCard = rail.querySelector(".folio-home-card");
        var railStyle = parentDocument.defaultView.getComputedStyle(rail);
        var gap = parseFloat(railStyle.columnGap || railStyle.gap || "0") || 0;
        var distance = firstCard ? firstCard.getBoundingClientRect().width + gap : Math.max(rail.clientWidth * 0.72, 320);
        rail.scrollBy({ left: direction * distance, behavior: "smooth" });
    });
})();
</script>
"""
_CARD_PREVIEW_SCRIPT = """
<script>
(function() {
    var parentDocument = window.parent.document;
    if (parentDocument.__folioCardPreviewBound) {
        return;
    }
    parentDocument.__folioCardPreviewBound = true;

    function mountPreview(preview) {
        if (!preview || preview.dataset.folioPreviewMounted === "1") {
            return;
        }
        var src = preview.getAttribute("data-folio-preview-src");
        if (!src) {
            return;
        }
        preview.dataset.folioPreviewMounted = "1";
        preview.classList.add("is-loaded");
        var iframe = parentDocument.createElement("iframe");
        iframe.className = "folio-home-card-preview-frame";
        iframe.title = "프로젝트 대시보드 미리보기";
        iframe.src = src;
        iframe.loading = "lazy";
        iframe.referrerPolicy = "no-referrer-when-downgrade";
        iframe.setAttribute("allowfullscreen", "true");
        preview.appendChild(iframe);
    }

    function alignPreviewCard(card) {
        var rail = card && card.closest(".folio-gallery-rail");
        if (!rail) {
            return;
        }
        card.classList.remove("folio-home-card-preview-align-left", "folio-home-card-preview-align-right");
        var cardRect = card.getBoundingClientRect();
        var railRect = rail.getBoundingClientRect();
        var sideExpansion = cardRect.width * 0.25;
        if (cardRect.right + sideExpansion > railRect.right) {
            card.classList.add("folio-home-card-preview-align-right");
        } else if (cardRect.left - sideExpansion < railRect.left) {
            card.classList.add("folio-home-card-preview-align-left");
        }
    }

    parentDocument.addEventListener("mouseenter", function(event) {
        var card = event.target.closest(".folio-home-card-has-preview");
        if (!card) {
            return;
        }
        alignPreviewCard(card);
        mountPreview(card.querySelector(".folio-home-card-preview"));
    }, true);

    parentDocument.addEventListener("focusin", function(event) {
        var card = event.target.closest(".folio-home-card-has-preview");
        if (!card) {
            return;
        }
        alignPreviewCard(card);
        mountPreview(card.querySelector(".folio-home-card-preview"));
    });
})();
</script>
"""
_COUNT_UP_SCRIPT = """
<script>
(function() {
    var parentDocument = window.parent.document;
    var attempts = 0;
    var maxAttempts = 40;

    function animateCounters() {
        var counters = parentDocument.querySelectorAll("[data-folio-count-up]");
        if (!counters.length && attempts < maxAttempts) {
            attempts += 1;
            parentDocument.defaultView.setTimeout(animateCounters, 50);
            return;
        }

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
    }

    animateCounters();
})();
</script>
"""


def render_count_up_script() -> None:
    _render_script(_COUNT_UP_SCRIPT)


def render_project_rails(
    rails: list[tuple[str, str, list[dict]]],
    *,
    home_page: str,
    extra_query_params: dict[str, str] | None = None,
) -> None:
    if not any(projects for _, _, projects in rails):
        render_rail_scroll_script()
        st.info("아직 표시할 프로젝트가 없습니다. 첫 프로젝트를 등록해보세요.")
        return

    for rail_key, description, projects in rails:
        render_project_rail(rail_key, description, projects, home_page=home_page, extra_query_params=extra_query_params)
    render_rail_scroll_script()
    render_card_preview_script()


def render_project_rail(
    rail_key: str,
    description: str,
    projects: list[dict],
    *,
    home_page: str,
    extra_query_params: dict[str, str] | None = None,
) -> None:
    cards_html = "".join(
        project_card_html(project, home_page=home_page, extra_query_params=extra_query_params)
        for project in projects
    )
    safe_rail_key = html.escape(rail_key, quote=True)
    safe_description = html.escape(description)
    title_html = _rail_title_html(rail_key, description)

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
                <h3>{title_html}</h3>
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


def _rail_title_html(rail_key: str, description: str) -> str:
    highlights = {
        "recent": "새로 공개",
        "views": "조회수",
        "likes": "좋아요",
    }
    highlight = highlights.get(rail_key)
    if not highlight or highlight not in description:
        return html.escape(description)

    before, after = description.split(highlight, 1)
    return (
        f"{html.escape(before)}"
        f'<span class="folio-gallery-rail-highlight">{html.escape(highlight)}</span>'
        f"{html.escape(after)}"
    )


def project_card_html(project: dict, *, home_page: str, extra_query_params: dict[str, str] | None = None) -> str:
    preview_url = normalize_power_bi_embed_url(project.get("power_bi_url"))
    params = {"page": home_page, **(extra_query_params or {}), "project_id": project["id"]}
    return render_project_card_html(
        project,
        compact=False,
        fallback_text=plain_text(project.get("insights")) or "",
        href=f"?{urlencode(params)}",
        preview_url=preview_url,
    )


def render_rail_scroll_script() -> None:
    _render_script(_RAIL_SCROLL_SCRIPT)


def render_card_preview_script() -> None:
    _render_script(_CARD_PREVIEW_SCRIPT)


def _render_script(script: str) -> None:
    components.html(script, height=0)
