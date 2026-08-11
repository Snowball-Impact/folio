"""Embedded dashboard preview component."""

from __future__ import annotations

import html
import json
from urllib.parse import urlparse

import streamlit.components.v1 as components


def render_embedded_dashboard(url: str) -> None:
    components.html(embedded_dashboard_html(url), height=embedded_dashboard_height(url))


def render_powerbi_report(report_id: str, embed_url: str, embed_token: str) -> None:
    components.html(
        powerbi_report_html(report_id, embed_url, embed_token),
        height=640,
    )


def embedded_dashboard_html(url: str) -> str:
    safe_url = html.escape(url, quote=True)
    min_height = embedded_dashboard_height(url) - 8
    return f"""
    <style>
        html,
        body {{
            margin: 0;
            overflow: auto;
            padding: 0;
        }}
        .folio-dashboard-frame {{
            align-items: flex-start;
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            min-height: {min_height}px;
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
            min-height: {min_height}px;
            inset: 0;
            justify-content: center;
            position: absolute;
            width: 100%;
            z-index: 1;
        }}
        .folio-dashboard-iframe {{
            background: #ffffff;
            border: 0;
            display: block;
            flex: 0 1 100%;
            height: {min_height}px;
            max-width: 100%;
            position: relative;
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


def powerbi_report_html(report_id: str, embed_url: str, embed_token: str) -> str:
    report_id_json = json.dumps(report_id)
    embed_url_json = json.dumps(embed_url)
    embed_token_json = json.dumps(embed_token)
    return f"""
    <style>
        html,
        body {{
            margin: 0;
            padding: 0;
        }}
        #folio-powerbi-report {{
            background: #ffffff;
            height: 632px;
            width: 100%;
        }}
        .folio-powerbi-error {{
            align-items: center;
            background: #f4f7fc;
            color: #60708f;
            display: none;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 14px;
            height: 632px;
            justify-content: center;
            text-align: center;
        }}
    </style>
    <div id="folio-powerbi-report"></div>
    <div class="folio-powerbi-error" id="folio-powerbi-error">
        Power BI 보고서를 불러오지 못했습니다.
    </div>
    <script src="https://cdn.jsdelivr.net/npm/powerbi-client@2.23.1/dist/powerbi.min.js"></script>
    <script>
        (function () {{
            function showError() {{
                var reportElement = document.getElementById("folio-powerbi-report");
                var errorElement = document.getElementById("folio-powerbi-error");
                if (reportElement) reportElement.style.display = "none";
                if (errorElement) errorElement.style.display = "flex";
            }}
            try {{
                var models = window["powerbi-client"].models;
                var reportContainer = document.getElementById("folio-powerbi-report");
                var config = {{
                    type: "report",
                    id: {report_id_json},
                    embedUrl: {embed_url_json},
                    accessToken: {embed_token_json},
                    tokenType: models.TokenType.Embed,
                    permissions: models.Permissions.Read,
                    settings: {{
                        panes: {{
                            filters: {{ visible: false }},
                            pageNavigation: {{ visible: true }}
                        }},
                        background: models.BackgroundType.Transparent
                    }}
                }};
                var report = window.powerbi.embed(reportContainer, config);
                report.on("error", showError);
            }} catch (error) {{
                showError();
            }}
        }})();
    </script>
    """


def embedded_dashboard_height(url: str) -> int:
    parsed = urlparse(url)
    if parsed.netloc.endswith("public.tableau.com"):
        return 1240
    return 520
