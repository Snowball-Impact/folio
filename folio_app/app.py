import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from folio_app.components.layout import render_header
from folio_app.config import get_settings
from folio_app.navigation import ROUTABLE_PAGES
from folio_app.pages import gallery, home, onboarding, protected
from folio_app.pages.auth import render_login, render_signup
from folio_app.services.profiles import get_onboarding_status
from folio_app.services.auth import (
    get_auth_tokens,
    get_current_user,
    restore_session,
    should_clear_browser_auth,
)
from folio_app.styles import apply_global_styles


def _initial_page_from_query() -> str | None:
    page = st.query_params.get("page")
    if page in ROUTABLE_PAGES:
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
        cookies.save()
        st.session_state.pop("folio_restore_failed", None)
        return

    access_token, refresh_token = get_auth_tokens()
    if access_token and refresh_token:
        if cookies.get("access_token") != access_token or cookies.get("refresh_token") != refresh_token:
            cookies["access_token"] = access_token
            cookies["refresh_token"] = refresh_token
            cookies.save()
        elif cookies.get("restore_failed") == "1":
            cookies.pop("restore_failed", None)
            cookies.save()


def _restore_auth_from_cookies(cookies: EncryptedCookieManager) -> None:
    if get_current_user() is not None:
        return

    if st.session_state.pop("folio_logout_in_progress", False):
        return

    access_token = cookies.get("access_token")
    refresh_token = cookies.get("refresh_token")
    if not access_token or not refresh_token:
        return

    result = restore_session(access_token, refresh_token)

    if not result.ok:
        cookies.pop("access_token", None)
        cookies.pop("refresh_token", None)
        cookies.save()
        current_page = st.query_params.get("page") or "Home"
        if current_page in {"Submit", "My Portfolio", "Profile"}:
            st.session_state["login_notice"] = result.message
            st.query_params.clear()
            st.query_params["page"] = "Login"
            st.rerun()
        return

    st.rerun()


def _normalize_legacy_routes() -> None:
    if st.query_params.get("page") == "Gallery":
        preserved = {key: st.query_params.get(key) for key in st.query_params}
        st.query_params.clear()
        st.query_params["page"] = "Home"
        for key, value in preserved.items():
            if key != "page" and value:
                st.query_params[key] = value
        st.rerun()


def _handle_logout_query() -> None:
    logout = st.query_params.get("logout")
    if logout == "1" or logout == ["1"]:
        from folio_app.services.auth import sign_out

        sign_out()
        st.query_params.clear()
        st.rerun()


def main() -> None:
    apply_global_styles()

    settings = get_settings()
    if not settings.is_supabase_configured:
        missing = ", ".join(settings.missing_supabase_settings)
        st.warning(
            f"Supabase 설정을 찾지 못했습니다: {missing}. "
            "Streamlit Cloud의 App settings > Secrets에서 키 이름과 저장 위치를 확인하세요."
        )

    cookies = _get_cookie_manager(settings)
    if not cookies.ready():
        st.stop()

    _handle_logout_query()
    _sync_browser_auth_storage(cookies)
    _restore_auth_from_cookies(cookies)
    _normalize_legacy_routes()
    _render_verified_notice()

    selected_page = render_header(initial_page=_initial_page_from_query())
    user = get_current_user()
    if user is not None:
        onboarding_done_key = f"onboarding_done_{user['id']}"
        if not st.session_state.get(onboarding_done_key):
            onboarding_status = get_onboarding_status(user["id"])
            if onboarding_status.error_message:
                st.error(onboarding_status.error_message)
                if st.button("다시 시도", key="retry_onboarding_status"):
                    st.rerun()
                st.markdown(
                    '<footer class="folio-footer"><p>Copyright &copy; 2026 Snowball Impact. All rights reserved.</p></footer>',
                    unsafe_allow_html=True,
                )
                return
            if onboarding_status.required and not onboarding_status.is_complete:
                onboarding.render(onboarding_status)
                st.markdown(
                    '<footer class="folio-footer"><p>Copyright &copy; 2026 Snowball Impact. All rights reserved.</p></footer>',
                    unsafe_allow_html=True,
                )
                return
            st.session_state[onboarding_done_key] = True

    page_handlers = {
        "Home": home.render,
        "Gallery": gallery.render,
        "Login": render_login,
        "Sign Up": render_signup,
        "Submit": protected.render_submit,
        "My Portfolio": protected.render_my_portfolio,
        "Profile": protected.render_profile,
    }

    page_handlers.get(selected_page, home.render)()

    st.markdown(
        '<footer class="folio-footer"><p>Copyright &copy; 2026 Snowball Impact. All rights reserved.</p></footer>',
        unsafe_allow_html=True,
    )
