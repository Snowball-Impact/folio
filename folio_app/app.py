import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from folio_app.components.layout import render_header
from folio_app.config import get_settings
from folio_app.pages import about, gallery, home, protected
from folio_app.pages.auth import render_login, render_signup
from folio_app.services.auth import (
    get_auth_tokens,
    get_current_user,
    restore_session,
    should_clear_browser_auth,
)
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


def _get_cookie_manager(settings) -> EncryptedCookieManager:
    return EncryptedCookieManager(
        prefix="folio/",
        password=settings.cookie_password,
    )


def _sync_browser_auth_storage(cookies: EncryptedCookieManager) -> None:
    if should_clear_browser_auth():
        cookies.pop("access_token", None)
        cookies.pop("refresh_token", None)
        cookies.pop("restore_failed", None)
        cookies.save()
        return

    access_token, refresh_token = get_auth_tokens()
    if access_token and refresh_token:
        if cookies.get("access_token") != access_token or cookies.get("refresh_token") != refresh_token:
            cookies["access_token"] = access_token
            cookies["refresh_token"] = refresh_token
            cookies.pop("restore_failed", None)
            cookies.save()


def _restore_auth_from_cookies(cookies: EncryptedCookieManager) -> None:
    if get_current_user() is not None:
        return

    if cookies.get("restore_failed") == "1":
        return

    access_token = cookies.get("access_token")
    refresh_token = cookies.get("refresh_token")
    if not access_token or not refresh_token:
        return

    result = restore_session(access_token, refresh_token)

    if not result.ok:
        cookies.pop("access_token", None)
        cookies.pop("refresh_token", None)
        cookies["restore_failed"] = "1"
        cookies.save()
        st.warning(result.message)
        return

    cookies.pop("restore_failed", None)
    cookies.save()
    st.rerun()


def _handle_logout_query() -> None:
    logout = st.query_params.get("logout")
    if logout == "1" or logout == ["1"]:
        from folio_app.services.auth import sign_out

        sign_out()
        st.query_params.clear()
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="FOLIO",
        page_icon="F",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_global_styles()

    settings = get_settings()
    if not settings.is_supabase_configured:
        st.warning(
            "Supabase 환경 변수가 아직 설정되지 않았습니다. "
            ".env.example을 참고해 .env를 만든 뒤 회원가입/로그인을 테스트하세요."
        )

    cookies = _get_cookie_manager(settings)
    if not cookies.ready():
        st.stop()

    _restore_auth_from_cookies(cookies)
    _sync_browser_auth_storage(cookies)
    _handle_logout_query()
    _render_verified_notice()

    selected_page = render_header(initial_page=_initial_page_from_query())

    page_handlers = {
        "Home": home.render,
        "Gallery": gallery.render,
        "Login": render_login,
        "Sign Up": render_signup,
        "About": about.render,
        "Submit": protected.render_submit,
        "My Portfolio": protected.render_my_portfolio,
        "Profile": protected.render_profile,
    }

    page_handlers.get(selected_page, home.render)()
