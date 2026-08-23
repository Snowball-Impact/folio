from __future__ import annotations

import html
import re
from datetime import datetime
from uuid import UUID, uuid4

import streamlit as st

from folio_app.components.project_comments import render_community_comments_section
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.community import (
    CATEGORY_LABELS,
    category_options_for_user,
    create_community_post,
    delete_community_post,
    get_community_post,
    increment_community_post_view_count,
    is_admin_user,
    list_community_posts,
    update_community_post,
)


_CATEGORY_FILTERS = [("all", "전체"), *CATEGORY_LABELS.items()]
_URL_PATTERN = re.compile(r"(https?://[^\s<]+)")


def render() -> None:
    user = get_current_user()
    post_id = st.query_params.get("post_id")
    edit_post_id = st.query_params.get("edit_post_id")
    if st.query_params.get("write") == "1" or edit_post_id:
        _render_editor(user, edit_post_id)
        return
    if post_id:
        _render_detail(post_id, user)
        return
    _render_list(user)


def _render_list(user: dict | None) -> None:
    current_category = st.query_params.get("category") or "all"
    if current_category not in dict(_CATEGORY_FILTERS):
        current_category = "all"

    notice = st.session_state.pop("community_notice", None)
    error = st.session_state.pop("community_error", None)

    with st.container(border=False, key="community_header"):
        st.markdown(
            """
            <section class="folio-community-hero">
                <div>
                    <span>FOLIO Community</span>
                    <h1>커뮤니티</h1>
                    <p>Power BI 사용자들과 질문과 경험을 나눠보세요.</p>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        if st.button("글쓰기", key="community_write_cta", type="primary"):
            if not user:
                st.session_state["login_notice"] = "커뮤니티 글을 작성하려면 로그인하세요."
                navigate("Login")
            navigate("Community", write="1")

    if notice:
        st.success(notice)
    if error:
        st.error(error)

    with st.container(border=False, key="community_filters"):
        cols = st.columns(len(_CATEGORY_FILTERS), gap="small")
        for column, (key, label) in zip(cols, _CATEGORY_FILTERS):
            with column:
                if st.button(label, key=f"community_filter_{key}", disabled=key == current_category, use_container_width=True):
                    params = {} if key == "all" else {"category": key}
                    navigate("Community", **params)

    posts = list_community_posts(None if current_category == "all" else current_category)
    if not posts:
        _render_empty_state(current_category, user)
        return

    st.markdown('<div class="folio-community-list">', unsafe_allow_html=True)
    for post in posts:
        _render_post_row(post)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_empty_state(category: str, user: dict | None) -> None:
    messages = {
        "question": ("아직 등록된 질문이 없습니다.", "궁금했던 내용을 가장 먼저 질문해보세요."),
        "tip": ("아직 공유된 노하우가 없습니다.", "다른 사용자에게 도움이 될 경험을 공유해보세요."),
        "other": ("아직 작성된 글이 없습니다.", ""),
        "notice": ("아직 등록된 공지가 없습니다.", ""),
        "all": ("아직 작성된 글이 없습니다.", "Power BI 사용자들과 첫 이야기를 나눠보세요."),
    }
    title, body = messages.get(category, messages["all"])
    st.markdown(
        f'<div class="folio-community-empty"><strong>{html.escape(title)}</strong><span>{html.escape(body)}</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("글쓰기", key="community_empty_write", use_container_width=False):
        if not user:
            st.session_state["login_notice"] = "커뮤니티 글을 작성하려면 로그인하세요."
            navigate("Login")
        else:
            navigate("Community", write="1")


def _render_post_row(post: dict) -> None:
    category = post.get("category") or "other"
    label = CATEGORY_LABELS.get(category, "기타")
    author = (post.get("author") or {}).get("name") or "작성자"
    created_at = _format_date(post.get("created_at"))
    comments = int(post.get("comment_count") or 0)
    views = int(post.get("view_count") or 0)
    pinned = '<span class="folio-community-pinned">고정</span>' if post.get("is_pinned") else ""
    row = (
        '<article class="folio-community-row">'
        f'<div class="folio-community-row-main">{pinned}<span class="folio-community-badge folio-community-badge-{html.escape(category)}">{html.escape(label)}</span>'
        f'<strong>{html.escape(post.get("title") or "제목 없음")}</strong></div>'
        f'<div class="folio-community-row-meta">{html.escape(author)} · {html.escape(created_at)} · 댓글 {comments} · 조회 {views}</div>'
        "</article>"
    )
    st.markdown(row, unsafe_allow_html=True)
    if st.button("게시글 보기", key=f"community_open_{post['id']}", use_container_width=True):
        navigate("Community", post_id=post["id"])


def _render_detail(post_id: str, user: dict | None) -> None:
    post = get_community_post(post_id, user.get("id") if user else None)
    if not post:
        st.error("게시글을 찾을 수 없습니다.")
        if st.button("커뮤니티로 돌아가기", key="community_missing_back"):
            navigate("Community")
        return

    _increment_view_once(post_id)

    notice = st.session_state.pop("community_notice", None)
    error = st.session_state.pop("community_error", None)
    if notice:
        st.success(notice)
    if error:
        st.error(error)

    author = (post.get("author") or {}).get("name") or "작성자"
    category = post.get("category") or "other"
    can_manage = bool(user and (user.get("id") == post.get("user_id") or is_admin_user(user.get("id"))))

    if st.button("← 커뮤니티", key="community_detail_back"):
        navigate("Community")

    st.markdown(
        (
            '<article class="folio-community-detail">'
            f'<div class="folio-community-detail-category">{html.escape(CATEGORY_LABELS.get(category, "기타"))}</div>'
            f'<h1>{html.escape(post.get("title") or "제목 없음")}</h1>'
            f'<div class="folio-community-detail-meta">{html.escape(author)} · {html.escape(_format_date(post.get("created_at")))} · 조회 {int(post.get("view_count") or 0)}</div>'
            f'<div class="folio-community-detail-body">{_linkify_text(post.get("content") or "")}</div>'
            "</article>"
        ),
        unsafe_allow_html=True,
    )

    if can_manage:
        with st.container(border=False, key="community_detail_actions", horizontal=True, gap="small"):
            if st.button("수정", key="community_edit_post"):
                navigate("Community", edit_post_id=post_id)
            delete_pending = bool(st.session_state.get(f"community_delete_confirm_{post_id}"))
            if st.button("삭제 확인" if delete_pending else "삭제", key="community_delete_post", type="primary" if delete_pending else "secondary"):
                if not delete_pending:
                    st.session_state[f"community_delete_confirm_{post_id}"] = True
                    st.rerun()
                result = delete_community_post(post_id, user["id"])
                if result.ok:
                    st.session_state["community_notice"] = "게시글이 삭제되었습니다."
                    navigate("Community")
                st.session_state["community_error"] = result.message
                st.rerun()
            if delete_pending and st.button("취소", key="community_cancel_delete_post"):
                st.session_state.pop(f"community_delete_confirm_{post_id}", None)
                st.rerun()

    render_community_comments_section(post_id, user, post.get("user_id"))


def _render_editor(user: dict | None, edit_post_id: str | None = None) -> None:
    if not user:
        st.session_state["login_notice"] = "커뮤니티 글을 작성하려면 로그인하세요."
        navigate("Login")
        return

    editing_post = get_community_post(edit_post_id, user.get("id")) if edit_post_id else None
    if edit_post_id and not editing_post:
        st.error("수정할 게시글을 찾을 수 없습니다.")
        if st.button("커뮤니티로 돌아가기", key="community_edit_missing_back"):
            navigate("Community")
        return

    if editing_post and editing_post.get("user_id") != user.get("id") and not is_admin_user(user.get("id")):
        st.error("게시글을 수정할 권한이 없습니다.")
        if st.button("커뮤니티로 돌아가기", key="community_edit_denied_back"):
            navigate("Community")
        return

    option_keys = category_options_for_user(user.get("id"))
    category_labels = [CATEGORY_LABELS[key] for key in option_keys]
    initial_category = (editing_post or {}).get("category") or option_keys[0]
    initial_index = option_keys.index(initial_category) if initial_category in option_keys else 0

    st.markdown(
        f'<section class="folio-community-editor-head"><span>{"수정" if editing_post else "글쓰기"}</span><h1>커뮤니티 게시글</h1></section>',
        unsafe_allow_html=True,
    )

    with st.form("community_post_form"):
        selected_label = st.selectbox("카테고리 *", category_labels, index=initial_index)
        title = st.text_input("제목 *", value=(editing_post or {}).get("title") or "", max_chars=120)
        content = st.text_area("내용 *", value=(editing_post or {}).get("content") or "", height=260, max_chars=5000)
        pinned = False
        if is_admin_user(user.get("id")):
            pinned = st.checkbox("상단 고정", value=bool((editing_post or {}).get("is_pinned")))
        cols = st.columns([1, 1, 4], gap="small")
        submitted = cols[0].form_submit_button("등록" if not editing_post else "수정", type="primary")
        cancelled = cols[1].form_submit_button("취소")

    if cancelled:
        if editing_post:
            navigate("Community", post_id=editing_post["id"])
        navigate("Community")

    if submitted:
        category = option_keys[category_labels.index(selected_label)]
        if editing_post:
            result = update_community_post(editing_post["id"], user["id"], category, title, content, is_pinned=pinned)
        else:
            result = create_community_post(user["id"], category, title, content, is_pinned=pinned)
        if result.ok and result.post_id:
            st.session_state["community_notice"] = result.message
            navigate("Community", post_id=result.post_id)
        st.error(result.message)


def _increment_view_once(post_id: str) -> None:
    viewed_key = f"community_viewed_{post_id}"
    if st.session_state.get(viewed_key):
        return
    visitor_id = st.session_state.get("folio_visitor_id") or _ensure_session_visitor_id()
    result = increment_community_post_view_count(post_id, visitor_id)
    st.session_state[viewed_key] = True
    if result.counted:
        st.rerun()


def _ensure_session_visitor_id() -> str:
    visitor_id = st.session_state.get("folio_visitor_id")
    try:
        visitor_id = str(UUID(visitor_id)) if visitor_id else ""
    except (TypeError, ValueError, AttributeError):
        visitor_id = ""
    if not visitor_id:
        visitor_id = str(uuid4())
    st.session_state["folio_visitor_id"] = visitor_id
    return visitor_id


def _linkify_text(value: str) -> str:
    escaped = html.escape(value or "")
    return _URL_PATTERN.sub(lambda match: f'<a href="{match.group(0)}" target="_blank" rel="noopener">{match.group(0)}</a>', escaped).replace("\n", "<br>")


def _format_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value.replace("T", " ")[:16]
    if parsed.tzinfo:
        parsed = parsed.astimezone()
    return parsed.strftime("%Y.%m.%d")
