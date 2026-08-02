"""Share button component used by project detail surfaces."""

from __future__ import annotations

import html
import json

import streamlit.components.v1 as components


def render_project_share_button(project_id: str) -> None:
    components.html(project_share_button_html(project_id), height=36)


def render_project_share_handler(project_id: str) -> None:
    components.html(project_share_handler_script(project_id), height=0)


def project_action_group_html(project_id: str, *, view_count: int, is_public: bool, comment_count: int = 0) -> str:
    visibility_label = "공개" if is_public else "비공개"
    visibility_class = "is-public" if is_public else "is-private"
    project_id_attr = html.escape(project_id, quote=True)
    return (
        '<div class="folio-detail-action-group">'
        f'<span class="folio-detail-action-chip" aria-label="조회수 {view_count}">조회 {view_count:,}</span>'
        f'<span class="folio-detail-action-chip" aria-label="댓글 {comment_count}">댓글 {comment_count:,}</span>'
        f'<span class="folio-detail-action-chip {visibility_class}">{visibility_label}</span>'
        f'<button class="folio-detail-share-button" type="button" data-folio-share-button data-project-id="{project_id_attr}" aria-label="공유 링크 복사">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
        '<path d="M10 13a5 5 0 0 0 7.07 0l2.83-2.83a5 5 0 0 0-7.07-7.07L11.5 4.43"></path>'
        '<path d="M14 11a5 5 0 0 0-7.07 0L4.1 13.83a5 5 0 0 0 7.07 7.07l1.33-1.33"></path>'
        "</svg>"
        '<span data-folio-share-label>링크 복사</span>'
        "</button>"
        "</div>"
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
            gap: 5px;
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
            min-width: 58px;
            padding: 0 10px;
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
            gap: 5px;
            height: 32px;
            justify-content: center;
            min-width: 88px;
            padding: 0 10px;
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


def project_share_handler_script(project_id: str) -> str:
    project_id_json = json.dumps(project_id)
    return f"""
    <script>
        (function() {{
            var parentDocument = window.parent.document;
            if (parentDocument.__folioShareHandlerBound) {{
                return;
            }}
            parentDocument.__folioShareHandlerBound = true;

            function setLabel(button, text) {{
                var label = button.querySelector("[data-folio-share-label]");
                if (!label) {{
                    return;
                }}
                label.textContent = text;
                window.setTimeout(function() {{ label.textContent = "링크 복사"; }}, 1600);
            }}

            function copyWithFallback(text) {{
                var input = parentDocument.createElement("textarea");
                input.value = text;
                input.setAttribute("readonly", "");
                input.style.position = "fixed";
                input.style.left = "-9999px";
                parentDocument.body.appendChild(input);
                input.select();
                var copied = parentDocument.execCommand("copy");
                parentDocument.body.removeChild(input);
                if (!copied) {{
                    throw new Error("copy failed");
                }}
            }}

            parentDocument.addEventListener("click", async function(event) {{
                var button = event.target.closest("[data-folio-share-button]");
                if (!button) {{
                    return;
                }}
                event.preventDefault();
                var projectId = button.getAttribute("data-project-id") || {project_id_json};
                var target = new URL(window.parent.location.origin + "/");
                target.searchParams.set("page", "Home");
                target.searchParams.set("project_id", projectId);
                target.searchParams.set("utm_source", "folio");
                target.searchParams.set("utm_medium", "share");
                target.searchParams.set("utm_campaign", "project_share");
                try {{
                    if (window.parent.navigator.clipboard && window.parent.navigator.clipboard.writeText) {{
                        await window.parent.navigator.clipboard.writeText(target.toString());
                    }} else {{
                        copyWithFallback(target.toString());
                    }}
                    setLabel(button, "복사 완료");
                }} catch (error) {{
                    setLabel(button, "복사 실패");
                }}
            }});
        }})();
    </script>
    """
