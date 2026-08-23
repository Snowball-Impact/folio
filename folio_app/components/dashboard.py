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
            flex-direction: column;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 14px;
            gap: 12px;
            min-height: {min_height}px;
            inset: 0;
            justify-content: center;
            position: absolute;
            text-align: center;
            width: 100%;
            z-index: 1;
        }}
        .folio-dashboard-placeholder strong {{
            color: #0b1f3f;
            font-size: 16px;
        }}
        .folio-dashboard-placeholder span {{
            max-width: 360px;
        }}
        .folio-dashboard-load-button {{
            background: #1459c8;
            border: 0;
            border-radius: 999px;
            color: #ffffff;
            cursor: pointer;
            font-family: inherit;
            font-size: 13px;
            font-weight: 700;
            min-height: 36px;
            padding: 0 18px;
        }}
        .folio-dashboard-load-button:disabled {{
            cursor: default;
            opacity: 0.72;
        }}
        .folio-dashboard-iframe {{
            background: #ffffff;
            border: 0;
            display: block;
            flex: 0 1 100%;
            height: {min_height}px;
            max-width: 100%;
            opacity: 0;
            position: relative;
            transition: opacity 0.18s ease;
            width: 100%;
            z-index: 2;
        }}
    </style>
    <div class="folio-dashboard-frame">
        <div class="folio-dashboard-placeholder" id="folio-dashboard-placeholder">
            <strong>대시보드 미리보기</strong>
            <span>외부 대시보드는 필요할 때만 불러와 상세페이지 첫 로딩을 가볍게 유지합니다.</span>
            <button class="folio-dashboard-load-button" id="folio-dashboard-load-button" type="button">
                대시보드 불러오기
            </button>
        </div>
        <iframe
            title="Embedded dashboard"
            data-src="{safe_url}"
            frameborder="0"
            allowFullScreen="true"
            class="folio-dashboard-iframe"
            onload="this.style.opacity='1'; var placeholder=document.getElementById('folio-dashboard-placeholder'); if (placeholder) placeholder.style.display='none';">
        </iframe>
    </div>
    <script>
        (function () {{
            var button = document.getElementById("folio-dashboard-load-button");
            var iframe = document.querySelector(".folio-dashboard-iframe");
            if (!button || !iframe) return;
            button.addEventListener("click", function () {{
                if (iframe.getAttribute("src")) return;
                button.disabled = true;
                button.textContent = "대시보드 불러오는 중...";
                iframe.setAttribute("src", iframe.getAttribute("data-src"));
            }});
        }})();
    </script>
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
