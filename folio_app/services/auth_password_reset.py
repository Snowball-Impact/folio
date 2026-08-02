from __future__ import annotations

import logging
from typing import Any

import streamlit as st
from supabase_auth.types import CodeExchangeParams, VerifyTokenHashParams

from folio_app.config import get_settings
from folio_app.services.auth_errors import friendly_auth_error
from folio_app.services.auth_session import (
    SESSION_CLEAR_BROWSER_AUTH_KEY,
    bind_password_reset_session,
    clear_local_auth_session,
    clear_password_reset_tokens,
)
from folio_app.services.auth_types import AuthResult
from folio_app.services.supabase_client import clear_supabase_client, get_supabase_client


logger = logging.getLogger(__name__)


def request_password_reset(email: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    settings = get_settings()

    try:
        client.auth.reset_password_for_email(
            email,
            {
                "redirect_to": settings.password_reset_redirect_url,
            },
        )
        return AuthResult(True, "비밀번호 재설정 메일 요청을 처리했습니다. 메일함과 스팸함을 확인하세요.")
    except Exception as exc:
        return AuthResult(False, friendly_auth_error("비밀번호 재설정", exc))


def complete_password_reset(access_token: str, refresh_token: str, new_password: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        session_response = client.auth.set_session(access_token, refresh_token)
        if session_response.session is None:
            return AuthResult(False, "비밀번호 재설정 링크가 만료되었습니다. 다시 요청하세요.")
        return update_password_and_clear_session(client, new_password)
    except Exception as exc:
        return AuthResult(False, friendly_auth_error("비밀번호 변경", exc))


def complete_password_reset_with_code(code: str, new_password: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        session_response = client.auth.exchange_code_for_session(CodeExchangeParams(auth_code=code))
        if session_response.session is None:
            return AuthResult(False, "비밀번호 재설정 링크가 만료되었습니다. 다시 요청하세요.")
        bind_password_reset_session(client, session_response.session)
        return update_password_and_clear_session(client, new_password)
    except Exception as exc:
        return AuthResult(False, friendly_auth_error("비밀번호 변경", exc))


def complete_password_reset_with_token_hash(token_hash: str, new_password: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        session_response = client.auth.verify_otp(
            VerifyTokenHashParams(type="recovery", token_hash=token_hash)
        )
        if session_response.session is None:
            return AuthResult(False, "비밀번호 재설정 링크가 만료되었습니다. 다시 요청하세요.")
        bind_password_reset_session(client, session_response.session)
        return update_password_and_clear_session(client, new_password)
    except Exception as exc:
        return AuthResult(False, friendly_auth_error("비밀번호 변경", exc))


def update_password_and_clear_session(client: Any, new_password: str) -> AuthResult:
    client.auth.update_user({"password": new_password})
    try:
        client.auth.sign_out()
    except Exception:
        logger.warning("Provider sign-out failed after password reset", exc_info=True)
    clear_local_auth_session()
    clear_password_reset_tokens()
    st.session_state[SESSION_CLEAR_BROWSER_AUTH_KEY] = True
    clear_supabase_client()
    return AuthResult(True, "비밀번호가 변경되었습니다. 새 비밀번호로 로그인하세요.")

