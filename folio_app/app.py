import streamlit as st

from folio_app.components.layout import render_header
from folio_app.config import get_settings
from folio_app.pages import about, gallery, home, protected
from folio_app.pages.auth import render_login, render_signup
from folio_app.styles import apply_global_styles


def _initial_page_from_query() -> str | None:
    page = st.query_params.get("page")
    if page in {"Home", "Gallery", "Login", "Sign Up", "About", "Submit", "My Portfolio", "Profile"}:
        return page
    return None


def _render_verified_notice() -> None:
    if st.query_params.get("verified") != "1":
        return

    st.success("이메일 인증이 완료되었습니다. 가입한 이메일과 비밀번호로 로그인하세요.")
    if st.button("확인", key="clear_verified_notice"):
        st.query_params.clear()
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="FOLIO",
        page_icon="F",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_styles()

    settings = get_settings()
    if not settings.is_supabase_configured:
        st.warning(
            "Supabase 환경 변수가 아직 설정되지 않았습니다. "
            ".env.example을 참고해 .env를 만든 뒤 회원가입/로그인을 테스트하세요."
        )

    _render_verified_notice()

    selected_page = render_header(initial_page=_initial_page_from_query())

    if selected_page == "Home":
        home.render()
    elif selected_page == "Gallery":
        gallery.render()
    elif selected_page == "Login":
        render_login()
    elif selected_page == "Sign Up":
        render_signup()
    elif selected_page == "About":
        about.render()
    elif selected_page == "Submit":
        protected.render_submit()
    elif selected_page == "My Portfolio":
        protected.render_my_portfolio()
    elif selected_page == "Profile":
        protected.render_profile()
    else:
        home.render()
