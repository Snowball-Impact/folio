import base64
import html
from functools import lru_cache
from pathlib import Path
from textwrap import dedent
from typing import Callable, Optional

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
    logo_src = _static_image_src("logo.png")

    with st.container(border=False, key="folio_header"):
        brand_col, nav_col = st.columns([5, 1])

        with brand_col:
            st.markdown(
                f'<div class="folio-header-logo"><img src="{logo_src}" alt="Folio"></div>',
                unsafe_allow_html=True,
            )
            if st.button("홈으로 이동", key="nav_brand_home"):
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
    image_name: Optional[str] = None,
    image_alt: str = "",
    image_html: str = "",
    footer_html: str = "",
    footer_actions: Optional[Callable[[], None]] = None,
    class_name: str = "",
) -> None:
    safe_eyebrow = html.escape(eyebrow)
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    footer_html = dedent(footer_html).strip()
    hero_class = "folio-page-hero folio-page-hero-dark" if dark else "folio-page-hero"
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
            f'<img src="{_static_image_src(image_name)}" alt="{html.escape(image_alt, quote=True)}" />'
            "</div>"
        )
    hero_markup = (
        f'<section class="{hero_class}">'
        '<div class="folio-page-hero-copy">'
        f'<div class="folio-page-hero-eyebrow">{safe_eyebrow}</div>'
        f'<h1>{safe_title}</h1>'
        f'<p class="folio-muted">{safe_body}</p>'
        f'{footer_html}'
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
