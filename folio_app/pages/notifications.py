from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from folio_app.components.layout import render_hero
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.notifications import list_notifications, mark_all_notifications_read, mark_notification_read


def render() -> None:
    user = get_current_user()
    render_hero(
        "Notifications",
        "알림",
        "내 프로젝트에 새로 들어온 반응을 확인하세요.",
        image_name="hero-my-page-v2.webp",
        image_alt="프로필 카드와 포트폴리오 통계를 표현한 3D 일러스트",
    )

    if not user:
        st.info("알림을 확인하려면 로그인이 필요합니다.")
        if st.button("로그인하기", key="notifications_login", use_container_width=True):
            navigate("Login")
        return

    notifications = list_notifications(user["id"])
    unread_exists = any(not item.get("is_read") for item in notifications)

    with st.container(border=True, key="notifications_panel"):
        st.markdown(
            """
            <div class="folio-notifications-heading">
                <h2>최근 알림</h2>
                <p>알림 페이지를 열면 새 알림은 읽음 처리됩니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not notifications:
            st.markdown(
                '<div class="folio-notifications-empty">아직 새 알림이 없습니다.</div>',
                unsafe_allow_html=True,
            )
            return

        for item in notifications:
            _render_notification_item(item, user["id"])

    if unread_exists:
        mark_all_notifications_read(user["id"])


def _render_notification_item(item: dict, user_id: str) -> None:
    is_read = bool(item.get("is_read"))
    title = html.escape(item.get("title") or "새 알림")
    created_at = html.escape(_format_timestamp(item.get("created_at")))
    state_label = "읽음" if is_read else "새 알림"
    state_class = "is-read" if is_read else "is-unread"

    with st.container(border=False, key=f"notification_item_{item['id']}"):
        st.markdown(
            f"""
            <div class="folio-notification-item {state_class}">
                <span class="folio-notification-state">{state_label}</span>
                <strong>{title}</strong>
                <time>{created_at}</time>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if item.get("project_id"):
            if st.button("프로젝트 보기", key=f"notification_open_{item['id']}", use_container_width=True):
                mark_notification_read(item["id"], user_id)
                navigate("Home", project_id=item["project_id"])


def _format_timestamp(value: str | None) -> str:
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return str(value)[:16]
    return parsed.astimezone().strftime("%Y-%m-%d %H:%M")
