from typing import Iterable

import streamlit as st

from folio_app.services.auth import get_current_user, is_authenticated, sign_out


def render_header(initial_page: str | None = None) -> str:
    user = get_current_user()

    left, right = st.columns([2, 1])
    with left:
        st.markdown("## FOLIO")
        st.markdown(
            "<div class='folio-nav-status'>발표로 끝나지 않는 프로젝트</div>",
            unsafe_allow_html=True,
        )

    with right:
        if user:
            email = user.get("email", "signed in")
            st.markdown(
                f"<div class='folio-nav-status'>로그인: {email}</div>",
                unsafe_allow_html=True,
            )
            if st.button("로그아웃", use_container_width=True):
                sign_out()
                st.rerun()
        else:
            st.markdown(
                "<div class='folio-nav-status'>방문자 모드</div>",
                unsafe_allow_html=True,
            )

    options = list(_navigation_options())
    index = options.index(initial_page) if initial_page in options else 0
    return st.sidebar.radio("Navigation", options, index=index, label_visibility="collapsed")


def _navigation_options() -> Iterable[str]:
    if is_authenticated():
        return [
            "Home",
            "Gallery",
            "Submit",
            "My Portfolio",
            "Profile",
        ]

    return [
        "Home",
        "Gallery",
        "Login",
        "Sign Up",
        "About",
    ]


def render_hero(eyebrow: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <section class="folio-hero">
            <div class="folio-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="folio-muted">{body}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder_card(title: str, body: str, metric: str | None = None) -> None:
    metric_html = f"<div class='folio-metric'>{metric}</div>" if metric else ""
    st.markdown(
        f"""
        <div class="folio-card">
            <h3>{title}</h3>
            <p class="folio-muted">{body}</p>
            {metric_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
