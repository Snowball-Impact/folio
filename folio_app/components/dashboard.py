"""Embedded dashboard preview component."""

from __future__ import annotations

import html

import streamlit.components.v1 as components


def render_embedded_dashboard(url: str) -> None:
    components.html(embedded_dashboard_html(url), height=520)


def embedded_dashboard_html(url: str) -> str:
    safe_url = html.escape(url, quote=True)
    return f"""
    <style>
        html,
        body {{
            margin: 0;
            overflow: hidden;
            padding: 0;
        }}
        .folio-dashboard-frame {{
            aspect-ratio: 16 / 9;
            position: relative;
            width: 100%;
        }}
        .folio-dashboard-placeholder {{
            align-items: center;
            background: #f4f7fc;
            color: #60708f;
            display: flex;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 14px;
            height: 100%;
            inset: 0;
            justify-content: center;
            position: absolute;
            width: 100%;
            z-index: 1;
        }}
        .folio-dashboard-iframe {{
            background: #ffffff;
            border: 0;
            height: 100%;
            inset: 0;
            position: absolute;
            width: 100%;
            z-index: 2;
        }}
    </style>
    <div class="folio-dashboard-frame">
        <div class="folio-dashboard-placeholder" id="folio-dashboard-placeholder">
            대시보드 불러오는 중...
        </div>
        <iframe
            title="Embedded dashboard"
            src="{safe_url}"
            frameborder="0"
            allowFullScreen="true"
            class="folio-dashboard-iframe"
            onload="var placeholder=document.getElementById('folio-dashboard-placeholder'); if (placeholder) placeholder.style.display='none';">
        </iframe>
    </div>
    """
