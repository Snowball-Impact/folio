from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.dashboard import render_embedded_dashboard
from folio_app.components.layout import render_hero
from folio_app.components.share import project_action_group_html, render_project_share_handler
from folio_app.components.ui import clean_html, is_http_url, render_project_cover_html
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.comments import (
    build_comment_tree,
    create_comment,
    delete_comment,
    list_project_comments,
    mark_project_comments_read,
)
from folio_app.services.project_content import sanitize_project_html
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    get_project,
    increment_view_count,
    is_project_liked,
    normalize_power_bi_embed_url,
    set_project_liked,
)

_HOME_PAGE = "Home"
_COMMENTS_PAGE_SIZE = 20


def render(project_id: str) -> None:
    notice = st.session_state.pop("project_notice", None)
    if notice:
        st.success(notice)

    _record_project_view(project_id)

    try:
        project = get_project(project_id)
    except ProjectServiceError as exc:
        st.error(str(exc))
        retry_col, back_col = st.columns(2)
        with retry_col:
            if st.button("다시 시도", key="retry_project_detail", use_container_width=True):
                clear_project_caches()
                st.rerun()
        with back_col:
            if st.button("목록으로 돌아가기", key="failed_detail_back", use_container_width=True):
                navigate(_HOME_PAGE)
        return
    if project is None:
        st.error("프로젝트를 찾을 수 없습니다.")
        if st.button("목록으로 돌아가기"):
            _clear_detail_query()
            st.rerun()
        return

    track_event("view_item", {"item_id": project_id, "item_name": project.get("title") or ""})
    _track_share_open(project_id)

    like_count = project.get("like_count", 0) or 0
    user = get_current_user()
    like_error = st.session_state.pop("detail_like_error", None)

    hero_description = project.get("one_liner") or "프로젝트 소개가 없습니다."

    render_hero(
        "프로젝트 상세",
        project.get("title") or "Untitled",
        hero_description,
        image_html=render_project_cover_html(project),
        footer_actions=lambda: _render_hero_footer_actions(project, project_id, like_count, user, like_error),
        class_name="folio-project-detail-hero",
    )

    visual_context = _project_visual_context(project)
    if visual_context["has_visual_panel"]:
        _render_project_visual_panel(
            project,
            visual_context["power_bi_url"],
            visual_context["has_report"],
            visual_context["has_github"],
        )

    report_sections = _project_report_sections(project)
    if not report_sections:
        st.info("아직 작성된 프로젝트 설명이 없습니다.")
    else:
        _render_sections(report_sections)

    _render_comments_section(project_id, user, project.get("author_id"))

    _render_back_to_gallery_action()


def _render_hero_footer_actions(
    project: dict,
    project_id: str,
    like_count: int,
    user: dict | None,
    like_error: str | None,
) -> None:
    if like_error:
        st.error(like_error)
    with st.container(
        border=False,
        key="detail_footer_row",
        horizontal=True,
        horizontal_alignment="left",
        vertical_alignment="center",
        gap="small",
    ):
        st.markdown(_hero_meta_html(project), unsafe_allow_html=True)
        st.markdown(
            project_action_group_html(
                project_id,
                view_count=project.get("view_count", 0) or 0,
                is_public=bool(project.get("is_public")),
                comment_count=project.get("comment_count", 0) or 0,
            ),
            unsafe_allow_html=True,
        )
        _render_detail_like_button(project_id, like_count, user)
        render_project_share_handler(project_id)


def _render_back_to_gallery_action() -> None:
    with st.container(
        border=False,
        key="detail_back_action_row",
        horizontal=True,
        horizontal_alignment="right",
        vertical_alignment="center",
    ):
        if st.button("← 홈 갤러리로 돌아가기", key="detail_content_back_button"):
            navigate(_HOME_PAGE)


def _hero_meta_html(project: dict) -> str:
    author = project.get("author") or {}
    author_name = author.get("name") or "작성자"
    author_org = author.get("organization") or ""
    created_at = project.get("created_at") or ""
    org_html = (
        f'<span class="folio-detail-meta-item folio-detail-org"><small>소속</small><strong>{html.escape(author_org)}</strong></span>'
        if author_org
        else ""
    )
    return clean_html(f"""
    <div class="folio-detail-summary">
        <div class="folio-detail-meta-row">
            <span class="folio-detail-meta-item folio-detail-author"><small>작성자</small><strong>{html.escape(author_name)}</strong></span>
            {org_html}
            <span class="folio-detail-meta-item folio-detail-date"><small>등록일</small><strong>{created_at[:10] if created_at else '정보 없음'}</strong></span>
        </div>
    </div>
    """)


def _record_project_view(project_id: str) -> None:
    viewed_key = f"viewed_{project_id}"
    visitor_id = st.session_state.get("folio_visitor_id")
    if visitor_id and not st.session_state.get(viewed_key):
        view_result = increment_view_count(project_id, visitor_id)
        if view_result.ok:
            st.session_state[viewed_key] = True


def _render_project_visual_panel(
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
        if power_bi_url:
            render_embedded_dashboard(power_bi_url)
            st.caption("화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.")
        elif project.get("power_bi_url"):
            st.warning("Power BI 임베드 주소를 확인하세요. iframe 코드 또는 https URL의 src 값이 필요합니다.")

        actions = _project_resource_actions(project, power_bi_url, has_report, has_github)
        if actions:
            action_cols = st.columns(len(actions), gap="medium")
            for action_col, (label, url) in zip(action_cols, actions):
                with action_col:
                    st.link_button(label, url, use_container_width=True)


def _project_visual_context(project: dict) -> dict[str, object]:
    power_bi_url = normalize_power_bi_embed_url(project.get("power_bi_url"))
    has_report = is_http_url(project.get("report_url"))
    has_github = is_http_url(project.get("github_url"))
    return {
        "power_bi_url": power_bi_url,
        "has_report": has_report,
        "has_github": has_github,
        "has_visual_panel": bool(power_bi_url or project.get("power_bi_url") or has_report or has_github),
    }


def _project_resource_actions(
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


def _render_detail_like_button(project_id: str, like_count: int, user: dict | None) -> None:
    if not user:
        if st.button(
            f"♡ 좋아요 {like_count}",
            key="detail_like_action",
            help="로그인 후 좋아요를 누를 수 있습니다.",
            use_container_width=False,
        ):
            navigate("Login")
        return

    try:
        liked = is_project_liked(project_id, user["id"])
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("좋아요 상태 다시 불러오기", key="retry_detail_like", use_container_width=True):
            clear_project_caches()
            st.rerun()
        return
    label = f"♥ 좋아요 {like_count}" if liked else f"♡ 좋아요 {like_count}"
    button_type = "primary" if liked else "secondary"
    if st.button(
        label,
        key="detail_like_action",
        type=button_type,
        use_container_width=False,
    ):
        result = set_project_liked(project_id, user["id"], not liked)
        if not result.ok:
            st.session_state["detail_like_error"] = result.message
        else:
            track_event("like" if not liked else "unlike", {"item_id": project_id})
        st.rerun()


def _render_comments_section(project_id: str, user: dict | None, project_author_id: str | None) -> None:
    comment_error = st.session_state.pop("comment_error", None)
    comment_notice = st.session_state.pop("comment_notice", None)

    comments = list_project_comments(project_id)
    if user and project_author_id and user.get("id") == project_author_id:
        mark_project_comments_read(project_id, user["id"])
    comment_tree = build_comment_tree(comments)
    comments_page_key = f"comments_page_{project_id}"
    total_pages = max(1, (len(comment_tree) + _COMMENTS_PAGE_SIZE - 1) // _COMMENTS_PAGE_SIZE)
    current_page = min(max(1, int(st.session_state.get(comments_page_key, 1))), total_pages)
    st.session_state[comments_page_key] = current_page
    page_start = (current_page - 1) * _COMMENTS_PAGE_SIZE
    page_end = page_start + _COMMENTS_PAGE_SIZE
    visible_comment_tree = comment_tree[page_start:page_end]

    with st.container(border=True, key="project_comments_section"):
        st.markdown(
            f'<div class="folio-comments-shell"><div class="folio-comments-heading"><h2>댓글 {len(comments)}개</h2><p>프로젝트에 대한 의견이나 질문을 남겨보세요.</p></div></div>',
            unsafe_allow_html=True,
        )

        if comment_error:
            st.error(comment_error)
        if comment_notice:
            st.success(comment_notice)

        _render_comment_form(project_id, user)
        st.markdown('<div class="folio-comments-divider"></div>', unsafe_allow_html=True)

        if not comment_tree:
            st.markdown(
                '<div class="folio-comments-empty"><strong>아직 댓글이 없습니다.</strong><span>첫 댓글로 프로젝트에 대한 의견이나 질문을 남겨보세요.</span></div>',
                unsafe_allow_html=True,
            )
            _render_comments_pagination(comments_page_key, current_page, total_pages)
            return

        for index, node in enumerate(visible_comment_tree, start=page_start + 1):
            _render_comment_node(node, user, project_id, project_author_id, level=0, index_label=str(index))

        _render_comments_pagination(comments_page_key, current_page, total_pages)


def _render_comment_form(project_id: str, user: dict | None) -> None:
    if not user:
        st.markdown(
            '<div class="folio-comments-login-note">로그인 후 댓글을 작성할 수 있습니다.</div>',
            unsafe_allow_html=True,
        )
        if st.button("로그인하기", key="comment_login_prompt", use_container_width=True):
            navigate("Login")
        return

    submit_label = "댓글 남기기"
    form_row = st.columns([4.3, 1.05], gap="small", vertical_alignment="center")
    body_col = form_row[0]
    button_col = form_row[1]

    with body_col:
        st.text_area(
            label="",
            key="comment_form_body",
            placeholder="댓글을 남겨보세요.",
            height=110,
            max_chars=1000,
        )

    with button_col:
        if st.button(
            submit_label,
            key="submit_comment",
            use_container_width=True,
        ):
            body = st.session_state.get("comment_form_body", "")
            if not body or not body.strip():
                st.session_state["comment_error"] = "댓글 내용을 입력하세요."
                st.rerun()
            result = create_comment(project_id, user["id"], body.strip(), parent_id=None)
            if not result.ok:
                st.session_state["comment_error"] = result.message
            else:
                st.session_state["comment_notice"] = "댓글이 등록되었습니다."
                st.session_state.pop("comment_form_body", None)
            st.rerun()


def _render_comments_pagination(page_key: str, current_page: int, total_pages: int) -> None:
    with st.container(
        border=False,
        key="comments_pagination",
        horizontal=True,
        horizontal_alignment="center",
        vertical_alignment="center",
        gap="small",
    ):
        if total_pages > 1:
            if st.button("이전", key="comments_page_prev", disabled=current_page <= 1, use_container_width=False):
                st.session_state[page_key] = current_page - 1
                st.rerun()
        st.markdown(
            f'<span class="folio-comments-page-status">{current_page if total_pages <= 1 else f"{current_page} / {total_pages}"}</span>',
            unsafe_allow_html=True,
        )
        if total_pages > 1:
            if st.button("다음", key="comments_page_next", disabled=current_page >= total_pages, use_container_width=False):
                st.session_state[page_key] = current_page + 1
                st.rerun()


def _render_reply_form(project_id: str, user: dict | None, reply_target_id: str | None, reply_target: dict) -> None:
    if not user or not reply_target_id:
        return

    target_author = reply_target.get("author") or {}
    target_name = target_author.get("name") or "작성자"
    reply_key = f"reply_form_body_{reply_target_id}"

    with st.container(border=False, key=f"reply_form_{reply_target_id}"):
        st.markdown(
            f'<div class="folio-reply-composer-head"><span>답글 작성</span><strong>{html.escape(target_name)}</strong><em>님에게 남기는 중</em></div>',
            unsafe_allow_html=True,
        )
        form_row = st.columns([4.3, 1.05], gap="small", vertical_alignment="center")
        with form_row[0]:
            st.text_area(
                label="",
                key=reply_key,
                placeholder="답글을 남겨보세요.",
                height=76,
                max_chars=1000,
            )
        with form_row[1]:
            if st.button(
                "취소",
                key=f"cancel_reply_{reply_target_id}",
                use_container_width=True,
            ):
                st.session_state.pop(reply_key, None)
                st.session_state.pop("comment_reply_target_id", None)
                st.rerun()
            if st.button(
                "답글 남기기",
                key=f"submit_reply_{reply_target_id}",
                use_container_width=True,
            ):
                body = st.session_state.get(reply_key, "")
                if not body or not body.strip():
                    st.session_state["comment_error"] = "댓글 내용을 입력하세요."
                    st.rerun()
                result = create_comment(project_id, user["id"], body.strip(), parent_id=reply_target_id)
                if not result.ok:
                    st.session_state["comment_error"] = result.message
                else:
                    st.session_state["comment_notice"] = "댓글이 등록되었습니다."
                    st.session_state.pop(reply_key, None)
                    st.session_state.pop("comment_reply_target_id", None)
                st.rerun()


def _render_comment_node(
    node: dict,
    user: dict | None,
    project_id: str,
    project_author_id: str | None,
    level: int,
    index_label: str,
) -> None:
    author = node.get("author") or {}
    author_name = author.get("name") or "작성자"
    created_at = _format_comment_timestamp(node.get("created_at"))
    is_project_author = bool(project_author_id and node.get("author_id") == project_author_id)
    author_badge = '<span class="folio-comment-author-badge">작성자</span>' if is_project_author else ""
    can_reply = bool(user and level == 0)
    can_delete = bool(user and user.get("id") == node.get("author_id"))
    has_actions = can_reply or can_delete
    confirm_delete_key = f"confirm_delete_comment_{node['id']}"
    delete_pending = bool(st.session_state.get(confirm_delete_key))
    row_kind = "reply" if level else "root"
    card_classes = [
        "folio-comment-card",
        "folio-comment-reply" if level else "",
        "folio-comment-has-actions" if has_actions else "",
    ]
    card_class = " ".join(class_name for class_name in card_classes if class_name)
    body = html.escape(node.get("body") or "")

    with st.container(border=False, key=f"comment_row_{row_kind}_{node['id']}"):
        st.markdown(
            f'<div class="{card_class}"><div class="folio-comment-line"><span class="folio-comment-index">{html.escape(index_label)}</span><div class="folio-comment-author-line"><strong>{html.escape(author_name)}</strong>{author_badge}</div><div class="folio-comment-body">{body}</div><span class="folio-comment-date">{html.escape(created_at)}</span></div></div>',
            unsafe_allow_html=True,
        )

        if has_actions:
            with st.container(
                border=False,
                key=f"comment_actions_{row_kind}_{node['id']}",
                horizontal=True,
                horizontal_alignment="right",
                vertical_alignment="center",
                gap="small",
            ):
                if can_reply:
                    if st.button("답글", key=f"reply_comment_{node['id']}", use_container_width=False):
                        st.session_state["comment_reply_target_id"] = node["id"]
                        st.rerun()
                if can_delete:
                    delete_label = "삭제 확인" if delete_pending else "삭제"
                    delete_type = "primary" if delete_pending else "secondary"
                    if st.button(
                        delete_label,
                        key=f"delete_comment_{node['id']}",
                        type=delete_type,
                        use_container_width=False,
                    ):
                        if not delete_pending:
                            st.session_state[confirm_delete_key] = True
                            st.rerun()
                        result = delete_comment(node["id"], user["id"])
                        if not result.ok:
                            st.session_state["comment_error"] = result.message
                        else:
                            st.session_state["comment_notice"] = "댓글이 삭제되었습니다."
                            st.session_state.pop(confirm_delete_key, None)
                        st.rerun()
                    if delete_pending:
                        if st.button("취소", key=f"cancel_delete_comment_{node['id']}", use_container_width=False):
                            st.session_state.pop(confirm_delete_key, None)
                            st.rerun()

        if user and st.session_state.get("comment_reply_target_id") == node.get("id"):
            _render_reply_form(project_id, user, node.get("id"), node)

        for child_index, child in enumerate(node.get("children") or [], start=1):
            _render_comment_node(
                child,
                user,
                project_id,
                project_author_id,
                level + 1,
                index_label=f"{index_label}.{child_index}",
            )


def _format_comment_timestamp(value: str | None) -> str:
    if not value:
        return ""

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value.replace("T", " ")[:16]

    if parsed.tzinfo:
        parsed = parsed.astimezone()
    return parsed.strftime("%Y-%m-%d %H:%M")


def _track_share_open(project_id: str) -> None:
    if st.query_params.get("utm_medium") != "share":
        return
    if st.query_params.get("utm_campaign") != "project_share":
        return

    tracked_key = f"tracked_share_open_{project_id}"
    if st.session_state.get(tracked_key):
        return

    st.session_state[tracked_key] = True
    track_event("project_share_open", {"item_id": project_id, "source": "copied_link"})


def _project_report_sections(project: dict) -> list[str]:
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


def _render_sections(sections: list[str]) -> None:
    st.markdown(
        _project_report_html(sections),
        unsafe_allow_html=True,
    )


def _project_report_html(sections: list[str]) -> str:
    section_html = "".join(_project_report_section_html(body) for body in sections)
    return clean_html(
        '<article class="folio-detail-content-card">'
        '<header class="folio-detail-content-heading"><h2>프로젝트 리포트</h2></header>'
        f"{section_html}</article>"
    )


def _project_report_section_html(body: str) -> str:
    return (
        '<section class="folio-detail-section">'
        f'<div class="folio-detail-section-content">{sanitize_project_html(body)}</div>'
        "</section>"
    )


def _clear_detail_query() -> None:
    navigate(_HOME_PAGE)
