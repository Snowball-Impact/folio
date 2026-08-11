"""Project detail visual resources and report rendering."""

from __future__ import annotations

import streamlit as st

from folio_app.components.dashboard import render_embedded_dashboard, render_powerbi_report
from folio_app.components.ui import clean_html, is_http_url
from folio_app.services.project_content import sanitize_project_html
from folio_app.services.powerbi import PowerBIServiceError, get_powerbi_embed_config
from folio_app.services.projects import normalize_power_bi_embed_url


def render_project_visual_panel(
    project: dict,
    power_bi_url: str | None,
    has_report: bool,
    has_github: bool,
) -> None:
    with st.container(border=False, key="project_detail_visual"):
        st.markdown(
            '<div class="folio-visual-heading"><h2>대표 결과물</h2></div>',
            unsafe_allow_html=True,
        )
        status = str(project.get("status") or "published")
        if status == "processing":
            st.info("Power BI 보고서를 게시하는 중입니다. 잠시 후 다시 확인하세요.")
        elif status == "failed":
            st.error("Power BI 보고서 게시에 실패했습니다. 프로젝트 작성자는 마이페이지에서 상태를 확인하세요.")
        elif project.get("project_type") == "powerbi" and project.get("id"):
            if not _render_powerbi_embedded_viewer(project):
                _render_fallback_dashboard(project, power_bi_url)
        elif power_bi_url:
            _render_fallback_dashboard(project, power_bi_url)
        elif project.get("power_bi_url"):
            st.warning("Power BI 임베드 주소를 확인하세요. iframe 코드 또는 https URL의 src 값이 필요합니다.")

        actions = project_resource_actions(project, power_bi_url, has_report, has_github)
        if actions:
            action_cols = st.columns(len(actions), gap="medium")
            for action_col, (label, url) in zip(action_cols, actions):
                with action_col:
                    st.link_button(label, url, use_container_width=True)


def project_visual_context(project: dict) -> dict[str, object]:
    power_bi_url = normalize_power_bi_embed_url(project.get("power_bi_url"))
    has_report = is_http_url(project.get("report_url"))
    has_github = is_http_url(project.get("github_url"))
    return {
        "power_bi_url": power_bi_url,
        "has_report": has_report,
        "has_github": has_github,
        "has_visual_panel": bool(
            project.get("status") in {"processing", "failed"}
            or power_bi_url
            or project.get("power_bi_url")
            or has_report
            or has_github
        ),
    }


def project_resource_actions(
    project: dict,
    power_bi_url: str | None,
    has_report: bool,
    has_github: bool,
) -> list[tuple[str, str]]:
    actions = []
    if power_bi_url:
        actions.append(("대시보드 열기 ↗", power_bi_url))
    if has_report:
        actions.append(("보고서 보기 ↗", project["report_url"]))
    if has_github:
        actions.append(("GitHub 보기 ↗", project["github_url"]))
    return actions


def _render_powerbi_embedded_viewer(project: dict) -> bool:
    try:
        embed_config = get_powerbi_embed_config(project["id"])
    except PowerBIServiceError as exc:
        st.error(str(exc))
        return False
    if embed_config is None:
        return False
    render_powerbi_report(embed_config.report_id, embed_config.embed_url, embed_config.embed_token)
    st.caption("Power BI Embed Token은 요청 시 발급되며 저장하지 않습니다.")
    return True


def _render_fallback_dashboard(project: dict, power_bi_url: str | None) -> None:
    if not power_bi_url:
        return
    render_embedded_dashboard(power_bi_url)
    st.caption("화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.")


def project_report_sections(project: dict) -> list[str]:
    return [
        body
        for body in [
            project.get("problem"),
            project.get("dataset"),
            project.get("process"),
            project.get("insights"),
        ]
        if body
    ]


def render_project_report_sections(sections: list[str]) -> None:
    st.markdown(
        project_report_html(sections),
        unsafe_allow_html=True,
    )


def project_report_html(sections: list[str]) -> str:
    section_html = "".join(project_report_section_html(body) for body in sections)
    return clean_html(
        '<article class="folio-detail-content-card">'
        '<header class="folio-detail-content-heading"><h2>프로젝트 리포트</h2></header>'
        f"{section_html}</article>"
    )


def project_report_section_html(body: str) -> str:
    return (
        '<section class="folio-detail-section">'
        f'<div class="folio-detail-section-content">{sanitize_project_html(body)}</div>'
        "</section>"
    )
