"""Project detail comment rendering."""

from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from folio_app.navigation import navigate
from folio_app.services.comments import (
    build_comment_tree,
    create_comment,
    delete_comment,
    list_project_comments,
    mark_project_comments_read,
)
from folio_app.services.notifications import mark_project_comment_notifications_read


_COMMENTS_PAGE_SIZE = 20


def render_comments_section(project_id: str, user: dict | None, project_author_id: str | None) -> None:
    comment_error = st.session_state.pop("comment_error", None)
    comment_notice = st.session_state.pop("comment_notice", None)

    comments = list_project_comments(project_id)
    if user and project_author_id and user.get("id") == project_author_id:
        mark_project_comments_read(project_id, user["id"])
        mark_project_comment_notifications_read(project_id, user["id"])
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
