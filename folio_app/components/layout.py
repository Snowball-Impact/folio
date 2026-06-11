import html

import streamlit as st

from folio_app.services.auth import get_current_user


def render_header(initial_page: str | None = None) -> str:
    user = get_current_user()
    options = list(_navigation_options())
    selected = initial_page if initial_page in _routable_pages() else "Home"
    labels = [_page_label(option) for option in options]

    nav_links = "".join(
        f"<a class='folio-nav-link{' folio-nav-link-active' if option == selected else ''}' href='?page={option}' target='_self'>{html.escape(label)}</a>"
        for option, label in zip(options, labels)
    )
    if user:
        nav_links += "<a class='folio-nav-link folio-nav-link-logout' href='?logout=1'>로그아웃</a>"

    st.markdown(
        f"""
        <header class="folio-topbar">
            <div class="folio-brand-group">
                <div class="folio-brand">FOLIO</div>
                <div class="folio-tagline">발표로 끝나지 않는 프로젝트</div>
            </div>
            <input type="checkbox" id="nav_toggle" class="folio-nav-toggle" />
            <label for="nav_toggle" class="folio-hamburger">☰</label>
            <nav class="folio-nav">
                {nav_links}
            </nav>
        </header>
        """,
        unsafe_allow_html=True,
    )

    return selected


def _navigation_options() -> list[str]:
    if get_current_user() is not None:
        return [
            "Home",
            "Gallery",
            "Submit",
            "My Portfolio",
            "Profile",
            "About",
        ]

    return [
        "Home",
        "Gallery",
        "Login",
        "About",
    ]


def _routable_pages() -> set[str]:
    return {
        "Home",
        "Gallery",
        "Login",
        "Sign Up",
        "About",
        "Submit",
        "My Portfolio",
        "Profile",
    }


def _page_label(page: str) -> str:
    return {
        "Home": "홈",
        "Gallery": "둘러보기",
        "Submit": "프로젝트 제출",
        "My Portfolio": "내 포트폴리오",
        "Profile": "프로필",
        "Login": "로그인",
        "Sign Up": "회원가입",
        "About": "소개",
    }.get(page, page)


def render_hero(eyebrow: str, title: str, body: str) -> None:
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    st.markdown(
        f"""
        <section class="folio-hero">
            <h1>{safe_title}</h1>
            <p class="folio-muted">{safe_body}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder_card(title: str, body: str, metric: str | None = None) -> None:
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    metric_html = f"<div class='folio-metric'>{html.escape(metric)}</div>" if metric else ""
    st.markdown(
        f"""
        <div class="folio-card">
            <h3>{safe_title}</h3>
            <p class="folio-muted">{safe_body}</p>
            {metric_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
