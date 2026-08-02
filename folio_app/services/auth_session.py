from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from folio_app.services.auth_types import AuthResult
from folio_app.services.supabase_client import clear_supabase_client, get_supabase_client


logger = logging.getLogger(__name__)


SESSION_USER_KEY = "folio_user"
SESSION_TOKEN_KEY = "folio_access_token"
SESSION_REFRESH_TOKEN_KEY = "folio_refresh_token"
SESSION_CLEAR_BROWSER_AUTH_KEY = "folio_clear_browser_auth"
SESSION_LOGOUT_IN_PROGRESS_KEY = "folio_logout_in_progress"
SESSION_PASSWORD_RESET_TOKEN_KEY = "folio_password_reset_access_token"
SESSION_PASSWORD_RESET_REFRESH_TOKEN_KEY = "folio_password_reset_refresh_token"


def get_current_user() -> dict[str, Any] | None:
    return st.session_state.get(SESSION_USER_KEY)


def sign_out() -> None:
    client = get_supabase_client()
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            logger.warning("Provider sign-out failed; local session will still be cleared", exc_info=True)

    clear_local_auth_session()
    st.session_state[SESSION_CLEAR_BROWSER_AUTH_KEY] = True
    st.session_state[SESSION_LOGOUT_IN_PROGRESS_KEY] = True
    clear_supabase_client()


def get_auth_tokens() -> tuple[str | None, str | None]:
    return (
        st.session_state.get(SESSION_TOKEN_KEY),
        st.session_state.get(SESSION_REFRESH_TOKEN_KEY),
    )


def get_password_reset_tokens() -> tuple[str | None, str | None]:
    return (
        st.session_state.get(SESSION_PASSWORD_RESET_TOKEN_KEY),
        st.session_state.get(SESSION_PASSWORD_RESET_REFRESH_TOKEN_KEY),
    )


def ensure_authenticated_session() -> AuthResult:
    """Rebind the stored user session to PostgREST before an authenticated mutation."""
    user = get_current_user()
    if user is None:
        return AuthResult(False, "로그인 정보가 만료되었습니다. 다시 로그인하세요.")

    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    access_token, refresh_token = get_auth_tokens()
    if not access_token or not refresh_token:
        restored = bind_current_client_session(client, user)
        if restored.ok:
            return restored
        return AuthResult(False, "로그인 정보가 만료되었습니다. 다시 로그인하세요.")

    try:
        response = client.auth.set_session(access_token, refresh_token)
        return bind_auth_response(client, response, user)
    except Exception:
        logger.exception("Failed to rebind authenticated session")

    try:
        response = client.auth.refresh_session(refresh_token)
        return bind_auth_response(client, response, user)
    except Exception:
        logger.exception("Failed to refresh authenticated session after set_session failure")

    restored = bind_current_client_session(client, user)
    if restored.ok:
        return restored
    return AuthResult(False, "로그인 정보가 만료되었습니다. 다시 로그인하세요.")


def bind_current_client_session(client: Any, expected_user: dict[str, Any]) -> AuthResult:
    try:
        session = client.auth.get_session()
    except Exception:
        logger.exception("Failed to read current client auth session")
        return AuthResult(False, "로그인 정보가 만료되었습니다. 다시 로그인하세요.")
    return bind_auth_response(client, session, expected_user)


def bind_auth_response(client: Any, response: Any, expected_user: dict[str, Any]) -> AuthResult:
    session = getattr(response, "session", None) or response
    if session is None:
        return AuthResult(False, "로그인 정보를 확인하지 못했습니다. 다시 로그인하세요.")

    access_token = getattr(session, "access_token", "")
    refresh_token = getattr(session, "refresh_token", "")
    if not access_token or not refresh_token:
        return AuthResult(False, "로그인 정보를 확인하지 못했습니다. 다시 로그인하세요.")

    auth_user = getattr(response, "user", None) or getattr(session, "user", None)
    if auth_user is None:
        try:
            user_response = client.auth.get_user(access_token)
            auth_user = getattr(user_response, "user", None)
        except Exception:
            logger.exception("Failed to load user for authenticated session")
            return AuthResult(False, "로그인 정보를 확인하지 못했습니다. 다시 로그인하세요.")

    auth_user_data = auth_user_to_dict(auth_user)
    if not auth_user_data:
        return AuthResult(False, "로그인 정보를 확인하지 못했습니다. 다시 로그인하세요.")
    if auth_user_data.get("id") != expected_user.get("id"):
        return AuthResult(False, "로그인 사용자 정보가 일치하지 않습니다. 다시 로그인하세요.")

    save_auth_session(session, auth_user_data)
    client.postgrest.auth(access_token)
    return AuthResult(True, "로그인 상태를 확인했습니다.")


def auth_user_to_dict(user: Any) -> dict[str, Any]:
    if isinstance(user, dict):
        return user
    if hasattr(user, "model_dump"):
        return user.model_dump()
    user_id = getattr(user, "id", None)
    if not user_id:
        return {}
    return {
        "id": user_id,
        "email": getattr(user, "email", ""),
        "user_metadata": getattr(user, "user_metadata", {}) or {},
    }


def should_clear_browser_auth() -> bool:
    return bool(st.session_state.pop(SESSION_CLEAR_BROWSER_AUTH_KEY, False))


def save_auth_session(session: Any, user: dict[str, Any]) -> None:
    st.session_state[SESSION_TOKEN_KEY] = session.access_token
    st.session_state[SESSION_REFRESH_TOKEN_KEY] = session.refresh_token
    st.session_state[SESSION_USER_KEY] = user


def clear_local_auth_session() -> None:
    st.session_state.pop(SESSION_TOKEN_KEY, None)
    st.session_state.pop(SESSION_REFRESH_TOKEN_KEY, None)
    st.session_state.pop(SESSION_USER_KEY, None)


def clear_password_reset_tokens() -> None:
    st.session_state.pop(SESSION_PASSWORD_RESET_TOKEN_KEY, None)
    st.session_state.pop(SESSION_PASSWORD_RESET_REFRESH_TOKEN_KEY, None)


def bind_password_reset_session(client: Any, session: Any) -> None:
    access_token = getattr(session, "access_token", "")
    refresh_token = getattr(session, "refresh_token", "")
    if access_token and refresh_token:
        st.session_state[SESSION_PASSWORD_RESET_TOKEN_KEY] = access_token
        st.session_state[SESSION_PASSWORD_RESET_REFRESH_TOKEN_KEY] = refresh_token
        client.auth.set_session(access_token, refresh_token)

