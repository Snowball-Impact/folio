import html
from typing import Callable, Optional

import streamlit as st

from folio_app.components.assets import static_image_src
from folio_app.navigation import ROUTABLE_PAGES, navigate
from folio_app.services.auth import get_current_user
from folio_app.services.notifications import (
    count_unread_notifications,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)
from folio_app.services.project_references import REFERENCE_PLATFORMS


def render_header(initial_page: str | None = None) -> str:
    user = get_current_user()
    selected = initial_page if initial_page in ROUTABLE_PAGES else "Home"
    current_page = st.query_params.get("page") or "Home"
    logo_src = static_image_src("logo.webp")
    unread_notification_count = count_unread_notifications(user["id"]) if user else 0
    if unread_notification_count:
        st.html(
            """
            <style>
            .st-key-nav_Notifications button::before {
                align-items: center;
                background: #dc2626;
                border: 1px solid rgba(255, 255, 255, 0.72);
                border-radius: 999px;
                color: #fff;
                content: "N";
                display: inline-flex;
                font-size: 9px;
                font-weight: 600;
                height: 15px;
                justify-content: center;
                line-height: 1;
                position: absolute;
                right: -10px;
                top: 2px;
                width: 15px;
            }
            </style>
            """
        )

    # No st.columns() here on purpose: Streamlit's column grid runs its own
    # ResizeObserver-based width measurement to decide wrapping, and that
    # measurement briefly overshoots-and-corrects on every resize/rerun,
    # producing a visible ~16px flicker on this sticky, always-visible
    # element. The header has exactly two real (in-flow) children -- the
    # brand group and the login button/menu popover -- laid out with plain
    # flexbox (row + space-between + align-items:center) on the existing
    # vertical block. Both are ordinary flex items sized to their own
    # content; only the invisible "홈으로 이동" hit-target overlaying the
    # logo needs position:absolute, and it's scoped to the small brand
    # wrapper below rather than the whole header.
    with st.container(border=False, key="folio_header"):
        with st.container(border=False, key="folio_header_brand"):
            st.markdown(
                f'<div class="folio-header-logo"><img src="{logo_src}" alt="Folio"></div>',
                unsafe_allow_html=True,
            )
            if st.button("홈으로 이동", key="nav_brand_home"):
                navigate("Home")

        with st.container(border=False, key="folio_header_nav"):
            nav_items = _header_nav_items(user is not None)
            for option, label in nav_items:
                if option == "Reference":
                    _render_reference_menu(current_page)
                    continue
                if option == "Notifications" and user:
                    _render_notifications_popover(user["id"], unread_notification_count)
                    continue
                is_active = option == current_page and option != "__logout__"
                if st.button(label, key=f"nav_{option}", disabled=is_active):
                    if option == "__logout__":
                        st.query_params.clear()
                        st.query_params["logout"] = "1"
                        st.rerun()
                    else:
                        navigate(option)

    return selected


def _header_nav_items(is_logged_in: bool) -> list[tuple[str, str]]:
    if not is_logged_in:
        return [
            ("Home", "홈 갤러리"),
            ("About", "서비스 소개"),
            ("Reference", "레퍼런스"),
            ("Power BI", "Power BI"),
            ("Submit", "프로젝트 등록"),
            ("Login", "로그인"),
        ]
    return [
        ("Home", "홈 갤러리"),
        ("About", "서비스 소개"),
        ("Reference", "레퍼런스"),
        ("Power BI", "Power BI"),
        ("Submit", "프로젝트 등록"),
        ("My Page", "마이 페이지"),
        ("__logout__", "로그아웃"),
        ("Notifications", "알림"),
    ]


def _render_reference_menu(current_page: str) -> None:
    active_platform = st.query_params.get("platform") or "tableau"
    with st.popover(
        "레퍼런스",
        key="nav_Reference",
        help="레퍼런스",
        width="content",
    ):
        for platform in REFERENCE_PLATFORMS:
            is_active = current_page == "Reference" and active_platform == platform.key
            if st.button(platform.label, key=f"nav_reference_{platform.key}", disabled=is_active, use_container_width=True):
                navigate("Reference", platform=platform.key)


def _render_notifications_popover(user_id: str, unread_count: int) -> None:
    label = "알림"
    with st.popover(
        label,
        icon=":material/notifications:",
        key="nav_Notifications",
        help="알림",
        width="content",
    ):
        notifications = list_notifications(user_id, limit=5)
        st.markdown(
            f"""
            <div class="folio-header-notifications-popover">
                <div class="folio-header-notifications-title">
                    <strong>알림</strong>
                    <span>{unread_count}개 새 알림</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not notifications:
            st.caption("아직 알림이 없습니다.")
        else:
            for item in notifications:
                state = "새 알림" if not item.get("is_read") else "읽음"
                st.markdown(
                    f"""
                    <div class="folio-header-notification-preview">
                        <span>{state}</span>
                        <strong>{html.escape(item.get("title") or "새 알림")}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if item.get("project_id"):
                    if st.button("보기", key=f"header_notification_open_{item['id']}", use_container_width=True):
                        mark_notification_read(item["id"], user_id)
                        navigate("Home", project_id=item["project_id"])
        if unread_count:
            if st.button("모두 읽음", key="header_notifications_mark_all", use_container_width=True):
                mark_all_notifications_read(user_id)
                st.rerun()
        if st.button("모두 보기", key="header_notifications_view_all", use_container_width=True):
            navigate("Notifications")


def render_hero(
    eyebrow: str,
    title: str,
    body: str,
    *,
    image_name: Optional[str] = None,
    image_alt: str = "",
    image_html: str = "",
    footer_actions: Optional[Callable[[], None]] = None,
    class_name: str = "",
) -> None:
    safe_eyebrow = html.escape(eyebrow)
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    hero_class = "folio-page-hero"
    if class_name:
        hero_class += f" {class_name}"
    if not image_name and not image_html:
        hero_class += " folio-page-hero-no-visual"
    visual_html = ""
    if image_html:
        visual_html = f"<div class=\"folio-page-hero-visual\">{image_html}</div>"
    elif image_name:
        visual_html = (
            '<div class="folio-page-hero-visual">'
            f'<img src="{static_image_src(image_name)}" alt="{html.escape(image_alt, quote=True)}" />'
            "</div>"
        )
    hero_markup = (
        f'<section class="{hero_class}">'
        '<div class="folio-page-hero-copy">'
        f'<div class="folio-page-hero-eyebrow">{safe_eyebrow}</div>'
        f'<h1>{safe_title}</h1>'
        f'<p class="folio-muted">{safe_body}</p>'
        '</div>'
        f'{visual_html}'
        '</section>'
    )
    st.markdown(
        hero_markup,
        unsafe_allow_html=True,
    )
    if footer_actions:
        with st.container(border=False, key="folio_hero_footer_actions"):
            footer_actions()
