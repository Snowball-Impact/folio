import base64
import html
from functools import lru_cache
from pathlib import Path

import streamlit as st

from folio_app.navigation import ROUTABLE_PAGES, navigate
from folio_app.services.auth import get_current_user


_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@lru_cache(maxsize=8)
def _static_image_src(image_name: str) -> str:
    image_path = _STATIC_DIR / image_name
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_header(initial_page: str | None = None) -> str:
    user = get_current_user()
    selected = initial_page if initial_page in ROUTABLE_PAGES else "Home"
    current_page = st.query_params.get("page") or "Home"

    with st.container(border=False, key="folio_header"):
        brand_col, nav_col = st.columns([5, 1])

        with brand_col:
            if st.button("FOLIO", key="nav_brand_home"):
                navigate("Home")

        with nav_col:
            if user is None:
                if st.button("로그인", key="nav_Login"):
                    navigate("Login")
            else:
                logged_in_nav = [
                    ("Submit", "프로젝트 제출"),
                    ("My Portfolio", "내 포트폴리오"),
                    ("Profile", "프로필"),
                    ("__logout__", "로그아웃"),
                ]
                with st.popover("☰"):
                    for option, label in logged_in_nav:
                        is_active = option == current_page and option != "__logout__"
                        if st.button(label, key=f"nav_{option}", use_container_width=True, disabled=is_active):
                            if option == "__logout__":
                                st.query_params.clear()
                                st.query_params["logout"] = "1"
                                st.rerun()
                            else:
                                navigate(option)

    return selected


def render_hero(
    eyebrow: str,
    title: str,
    body: str,
    *,
    dark: bool = False,
    image_name: str | None = None,
    image_alt: str = "",
) -> None:
    safe_eyebrow = html.escape(eyebrow)
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    hero_class = "folio-page-hero folio-page-hero-dark" if dark else "folio-page-hero"
    visual_html = ""
    if image_name:
        visual_html = (
            '<div class="folio-page-hero-visual">'
            f'<img src="{_static_image_src(image_name)}" alt="{html.escape(image_alt, quote=True)}" />'
            "</div>"
        )
    st.markdown(
        f"""
        <section class="{hero_class}">
            <div class="folio-page-hero-copy">
                <div class="folio-page-hero-eyebrow">{safe_eyebrow}</div>
                <h1>{safe_title}</h1>
                <p class="folio-muted">{safe_body}</p>
            </div>
            {visual_html}
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
