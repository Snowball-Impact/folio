from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st

from folio_app.config import get_settings
from folio_app.services.profiles import ensure_profile, profile_exists_for_email
from folio_app.services.supabase_client import clear_supabase_client, get_supabase_client


SESSION_USER_KEY = "folio_user"
SESSION_TOKEN_KEY = "folio_access_token"
SESSION_REFRESH_TOKEN_KEY = "folio_refresh_token"
SESSION_CLEAR_BROWSER_AUTH_KEY = "folio_clear_browser_auth"


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    message: str


def get_current_user() -> dict[str, Any] | None:
    return st.session_state.get(SESSION_USER_KEY)


def is_authenticated() -> bool:
    return get_current_user() is not None


def sign_up(email: str, password: str, name: str, organization: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    settings = get_settings()

    try:
        if profile_exists_for_email(email):
            return AuthResult(False, "이미 가입된 이메일입니다. Login 메뉴에서 로그인하세요.")

        response = client.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": settings.login_redirect_url,
                    "data": {
                        "name": name,
                        "organization": organization,
                    }
                },
            }
        )
        if response.user is None:
            return AuthResult(False, "회원가입 응답에서 사용자 정보를 찾을 수 없습니다.")

        if response.session:
            _save_auth_session(response.session, response.user.model_dump())
            ensure_profile(response.user.id, email, name, organization)
            return AuthResult(True, "회원가입이 완료되었습니다.")

        return AuthResult(True, "회원가입이 완료되었습니다. 이메일 인증 후 로그인하세요.")
    except Exception as exc:  # Supabase client raises provider-specific exceptions.
        return AuthResult(False, _friendly_auth_error("회원가입", exc))


def sign_in(email: str, password: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        response = client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        if response.user is None or response.session is None:
            return AuthResult(False, "이메일 또는 비밀번호를 확인하세요.")

        _save_auth_session(response.session, response.user.model_dump())

        metadata = response.user.user_metadata or {}
        try:
            ensure_profile(
                response.user.id,
                response.user.email or email,
                metadata.get("name", ""),
                metadata.get("organization", ""),
            )
        except Exception:
            # Login has already succeeded. Profile repair can be retried elsewhere.
            pass
        return AuthResult(True, "로그인되었습니다.")
    except Exception as exc:
        return AuthResult(False, _friendly_auth_error("로그인", exc))


def resend_signup_confirmation(email: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    settings = get_settings()

    try:
        client.auth.resend(
            {
                "type": "signup",
                "email": email,
                "options": {
                    "email_redirect_to": settings.login_redirect_url,
                },
            }
        )
        return AuthResult(True, "인증 메일을 다시 보냈습니다. 메일함과 스팸함을 확인하세요.")
    except Exception as exc:
        return AuthResult(False, _friendly_auth_error("인증 메일 재발송", exc))


def sign_out() -> None:
    client = get_supabase_client()
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass

    st.session_state.pop(SESSION_TOKEN_KEY, None)
    st.session_state.pop(SESSION_REFRESH_TOKEN_KEY, None)
    st.session_state.pop(SESSION_USER_KEY, None)
    st.session_state[SESSION_CLEAR_BROWSER_AUTH_KEY] = True
    clear_supabase_client()


def restore_session(access_token: str, refresh_token: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        response = client.auth.set_session(access_token, refresh_token)
        if response.user is None or response.session is None:
            return AuthResult(False, "저장된 로그인 정보를 복원하지 못했습니다. 다시 로그인하세요.")

        _save_auth_session(response.session, response.user.model_dump())

        metadata = response.user.user_metadata or {}
        ensure_profile(
            response.user.id,
            response.user.email or "",
            metadata.get("name", ""),
            metadata.get("organization", ""),
        )
        return AuthResult(True, "로그인 상태를 복원했습니다.")
    except Exception as exc:
        return AuthResult(False, _friendly_auth_error("로그인 복원", exc))


def get_auth_tokens() -> tuple[str | None, str | None]:
    return (
        st.session_state.get(SESSION_TOKEN_KEY),
        st.session_state.get(SESSION_REFRESH_TOKEN_KEY),
    )


def should_clear_browser_auth() -> bool:
    return bool(st.session_state.pop(SESSION_CLEAR_BROWSER_AUTH_KEY, False))


def _save_auth_session(session: Any, user: dict[str, Any]) -> None:
    st.session_state[SESSION_TOKEN_KEY] = session.access_token
    st.session_state[SESSION_REFRESH_TOKEN_KEY] = session.refresh_token
    st.session_state[SESSION_USER_KEY] = user


def _friendly_auth_error(action: str, exc: Exception) -> str:
    message = str(exc)
    normalized = message.lower()

    if "email rate limit exceeded" in normalized:
        return "인증 메일 발송 요청이 잠시 제한되었습니다. 잠시 후 다시 시도하세요."
    if "invalid email" in normalized or "email address" in normalized:
        return "올바른 이메일 주소를 입력하세요."
    if "already registered" in normalized or "user already registered" in normalized:
        return "이미 가입된 이메일입니다. 로그인하거나 인증 메일을 확인하세요."
    if "email not confirmed" in normalized:
        return "이메일 인증이 아직 완료되지 않았습니다. 인증 메일을 확인하세요."
    if "invalid login credentials" in normalized:
        return "이메일 또는 비밀번호를 확인하세요."
    if "refresh token" in normalized:
        return "저장된 로그인 정보가 만료되었습니다. 다시 로그인하세요."
    if (
        "getaddrinfo failed" in normalized
        or "connecterror" in normalized
        or "temporary failure in name resolution" in normalized
        or "name or service not known" in normalized
    ):
        return "Supabase 서버에 연결하지 못했습니다. .env의 SUPABASE_URL 또는 네트워크/DNS 상태를 확인하세요."

    return f"{action}에 실패했습니다. 잠시 후 다시 시도하세요. ({message})"
