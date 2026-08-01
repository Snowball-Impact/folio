"""Share button component used by project detail surfaces."""

from __future__ import annotations

import json

import streamlit.components.v1 as components


def render_project_share_button(project_id: str) -> None:
    components.html(project_share_button_html(project_id), height=36)


def render_project_action_group(project_id: str, *, view_count: int, is_public: bool) -> None:
    components.html(project_action_group_html(project_id, view_count=view_count, is_public=is_public), height=36)


def project_action_group_html(project_id: str, *, view_count: int, is_public: bool) -> str:
    visibility_label = "공개" if is_public else "비공개"
    visibility_class = "is-public" if is_public else "is-private"
    return project_share_button_html(
        project_id,
        leading_html=(
            f'<span class="folio-action-chip" aria-label="조회수 {view_count}">조회 {view_count:,}</span>'
            f'<span class="folio-action-chip {visibility_class}">{visibility_label}</span>'
        ),
    )


def project_share_button_html(project_id: str, *, leading_html: str = "") -> str:
    project_id_json = json.dumps(project_id)
    return f"""
    <style>
        html,
        body {{
            align-items: center;
            background: transparent;
            display: flex;
            height: 36px;
            justify-content: flex-end;
            margin: 0;
            overflow: hidden;
            padding: 0;
        }}
        .folio-action-group {{
            align-items: center;
            display: inline-flex;
            gap: 6px;
            height: 36px;
            justify-content: flex-end;
            white-space: nowrap;
            width: 100%;
        }}
        .folio-action-chip {{
            align-items: center;
            background: #ffffff;
            border: 1px solid #dce5f7;
            border-radius: 999px;
            color: #1459c8;
            display: inline-flex;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 12px;
            font-weight: 700;
            height: 32px;
            justify-content: center;
            line-height: 1;
            min-width: 64px;
            padding: 0 12px;
        }}
        .folio-action-chip.is-public {{
            background: #e7f6f2;
            border-color: #d2eee8;
            color: #087568;
        }}
        .folio-action-chip.is-private {{
            background: #edf0f5;
            border-color: #d8dee9;
            color: #65748a;
        }}
        .folio-share-button {{
            align-items: center;
            background: #ffffff;
            border: 1px solid #dce5f7;
            border-radius: 999px;
            color: #1459c8;
            cursor: pointer;
            display: inline-flex;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 12px;
            font-weight: 700;
            gap: 6px;
            height: 32px;
            justify-content: center;
            min-width: 96px;
            padding: 0 12px;
            transition: background 0.14s ease, border-color 0.14s ease, color 0.14s ease;
            width: auto;
        }}
        .folio-share-button:hover {{
            background: #eef3fd;
            border-color: rgba(20, 89, 200, 0.35);
        }}
        .folio-share-button svg {{
            height: 14px;
            width: 14px;
        }}
    </style>
    <div class="folio-action-group">
        {leading_html}
        <button class="folio-share-button" type="button" id="folio-share-button" aria-label="공유 링크 복사">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M10 13a5 5 0 0 0 7.07 0l2.83-2.83a5 5 0 0 0-7.07-7.07L11.5 4.43"></path>
                <path d="M14 11a5 5 0 0 0-7.07 0L4.1 13.83a5 5 0 0 0 7.07 7.07l1.33-1.33"></path>
            </svg>
            <span id="folio-share-label">링크 복사</span>
        </button>
    </div>
    <script>
        (function() {{
            var projectId = {project_id_json};
            var button = document.getElementById("folio-share-button");
            var label = document.getElementById("folio-share-label");
            function setLabel(text) {{
                label.textContent = text;
                window.setTimeout(function() {{ label.textContent = "링크 복사"; }}, 1600);
            }}
            function copyWithFallback(text) {{
                var input = document.createElement("textarea");
                input.value = text;
                input.setAttribute("readonly", "");
                input.style.position = "fixed";
                input.style.left = "-9999px";
                document.body.appendChild(input);
                input.select();
                var copied = document.execCommand("copy");
                document.body.removeChild(input);
                if (!copied) {{
                    throw new Error("copy failed");
                }}
            }}
            button.addEventListener("click", async function() {{
                var target = new URL(window.parent.location.origin + "/");
                target.searchParams.set("page", "Home");
                target.searchParams.set("project_id", projectId);
                target.searchParams.set("utm_source", "folio");
                target.searchParams.set("utm_medium", "share");
                target.searchParams.set("utm_campaign", "project_share");
                try {{
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        await navigator.clipboard.writeText(target.toString());
                    }} else {{
                        copyWithFallback(target.toString());
                    }}
                    setLabel("복사 완료");
                }} catch (error) {{
                    setLabel("복사 실패");
                }}
            }});
        }})();
    </script>
    """
