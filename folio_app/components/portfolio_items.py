"""Portfolio item rendering for My Page."""

from __future__ import annotations

import html

import streamlit as st

from folio_app.components.ui import clean_html, render_project_metrics, render_tag_chips


def render_portfolio_item(project: dict) -> None:
    st.markdown(portfolio_item_html(project), unsafe_allow_html=True)


def portfolio_item_html(project: dict) -> str:
    title = html.escape(project.get("title") or "Untitled")
    one_liner = html.escape(project.get("one_liner") or "")
    tags_html = render_tag_chips(project.get("tags") or [])
    unread_badge = (
        '<span class="folio-portfolio-card-new-badge" aria-label="안 본 댓글 있음">NEW</span>'
        if project.get("has_unread_comments")
        else ""
    )
    is_public = bool(project.get("is_public"))
    visibility_label = "공개" if is_public else "비공개"
    visibility_icon = (
        '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"></path></svg>'
        if is_public
        else '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"></rect><path d="M8 10V7a4 4 0 0 1 8 0v3"></path></svg>'
    )
    metrics_html = render_project_metrics(
        project,
        container_class="folio-portfolio-card-meta",
        extra_html=f'<span title="{visibility_label}" aria-label="공개 상태 {visibility_label}">{visibility_icon}</span>',
    )
    liner_html = f"<p class='folio-portfolio-card-liner'>{one_liner}</p>" if one_liner else ""

    return clean_html(f"""
    <div class="folio-portfolio-card">
        <div class="folio-portfolio-card-main">
            <p class="folio-portfolio-card-title"><span>{title}</span>{unread_badge}</p>
            {liner_html}
        </div>
        <div class="folio-portfolio-card-footer">
            {tags_html}
            {metrics_html}
        </div>
    </div>
    """)
