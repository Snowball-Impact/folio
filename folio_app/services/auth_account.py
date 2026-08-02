from __future__ import annotations

import logging

from folio_app.config import get_settings
from folio_app.services.auth_errors import friendly_auth_error
from folio_app.services.auth_session import save_auth_session
from folio_app.services.auth_types import AuthResult
from folio_app.services.profiles import (
    ProfileServiceError,
    complete_onboarding,
    ensure_profile,
    profile_exists_for_email,
)
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


def sign_up(
    email: str,
    password: str,
    name: str,
    organization: str,
    consented_policy_version_ids: list[str] | None = None,
) -> AuthResult:
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
                        "consented_policy_version_ids": consented_policy_version_ids or [],
                    }
                },
            }
        )
        if response.user is None:
            return AuthResult(False, "회원가입 응답에서 사용자 정보를 찾을 수 없습니다.")
        if sign_up_response_indicates_existing_user(response.user):
            return AuthResult(False, "이미 가입된 이메일입니다. Login 메뉴에서 로그인하세요.")

        if response.session:
            save_auth_session(response.session, response.user.model_dump())
            ensure_profile(response.user.id, email, name, organization)
            apply_pending_policy_consents(response.user.id, consented_policy_version_ids or [])
            return AuthResult(True, "회원가입이 완료되었습니다.")

        return AuthResult(True, "회원가입 요청을 처리했습니다. 메일함을 확인하세요.")
    except Exception as exc:  # Supabase client raises provider-specific exceptions.
        return AuthResult(False, friendly_auth_error("회원가입", exc))


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

        save_auth_session(response.session, response.user.model_dump())

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
            logger.exception("Login succeeded but profile repair failed")
        apply_pending_policy_consents(response.user.id, metadata.get("consented_policy_version_ids") or [])
        return AuthResult(True, "로그인되었습니다.")
    except Exception as exc:
        return AuthResult(False, friendly_auth_error("로그인", exc))


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
        return AuthResult(True, "인증 메일 재발송 요청을 처리했습니다. 메일함과 스팸함을 확인하세요.")
    except Exception as exc:
        return AuthResult(False, friendly_auth_error("인증 메일 재발송", exc))


def sign_up_response_indicates_existing_user(user) -> bool:
    identities = getattr(user, "identities", None)
    if identities == []:
        return True

    if hasattr(user, "model_dump"):
        try:
            user_data = user.model_dump()
        except Exception:
            return False
        return user_data.get("identities") == []

    return False


def apply_pending_policy_consents(user_id: str, policy_version_ids: list[str]) -> None:
    if not policy_version_ids:
        return
    try:
        complete_onboarding(user_id, policy_version_ids)
    except ProfileServiceError:
        # Onboarding page remains as a fallback if this silent completion fails.
        logger.exception("Failed to apply signup-time policy consents")

