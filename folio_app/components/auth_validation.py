import logging

import streamlit as st

from folio_app.services.profiles import get_required_policy_versions, profile_exists_for_email


logger = logging.getLogger(__name__)


EXISTING_ACCOUNT_MESSAGE_PREFIX = "이미 가입된 이메일"


class SignupEmailCheckError(RuntimeError):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_valid_email(email: str) -> bool:
    if not email or "@" not in email:
        return False

    local, _, domain = email.partition("@")
    return bool(local and "." in domain and not domain.startswith(".") and not domain.endswith("."))


@st.cache_data(ttl=10, show_spinner=False)
def cached_profile_exists_for_email(email: str) -> bool:
    return profile_exists_for_email(email)


@st.cache_data(ttl=60, show_spinner=False)
def cached_required_policy_versions() -> dict:
    return get_required_policy_versions()


def signup_required_policies() -> dict:
    try:
        return cached_required_policy_versions()
    except Exception:
        # Signup should not be blocked by a policy-fetch failure; onboarding
        # after first login remains the fallback for collecting consent.
        logger.exception("Failed to load policy versions for signup")
        return {}


def email_already_registered(email: str) -> bool:
    if not is_valid_email(email):
        return False

    try:
        return cached_profile_exists_for_email(email)
    except Exception as exc:
        raise SignupEmailCheckError("가입 여부를 확인하지 못했습니다. 잠시 후 다시 시도하세요.") from exc


def signup_missing_required_fields(
    email: str,
    password: str,
    password_confirm: str,
    name: str,
    organization: str,
) -> list[str]:
    return [
        label
        for label, value in {
            "이메일": email,
            "비밀번호": password,
            "비밀번호 확인": password_confirm,
            "이름": name,
            "소속": organization,
        }.items()
        if not value
    ]


def is_existing_account_message(message: str) -> bool:
    return message.startswith(EXISTING_ACCOUNT_MESSAGE_PREFIX)

