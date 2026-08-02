import logging

import streamlit as st

from folio_app.components.auth_forms import (
    query_value as _query_value,
    render_auth_card_header as _render_auth_card_header,
    render_email_feedback as _render_email_feedback,
    render_login,
    render_login_secondary_actions as _render_login_secondary_actions,
    render_password_confirm_feedback as _render_password_confirm_feedback,
    render_password_feedback as _render_password_feedback,
    render_password_reset_form as _render_password_reset_form,
    render_password_update_form as _render_password_update_form,
    render_signup,
    render_signup_login_link as _render_signup_login_link,
    resend_cooldown_remaining as _resend_cooldown_remaining,
)
from folio_app.components.auth_validation import (
    EXISTING_ACCOUNT_MESSAGE_PREFIX,
    SignupEmailCheckError,
    cached_profile_exists_for_email as _cached_profile_exists_for_email,
    cached_required_policy_versions as _cached_required_policy_versions,
    is_valid_email as _is_valid_email,
    normalize_email as _normalize_email,
    signup_missing_required_fields as _signup_missing_required_fields,
)


logger = logging.getLogger(__name__)


def _signup_required_policies() -> dict:
    try:
        return _cached_required_policy_versions()
    except Exception:
        logger.exception("Failed to load policy versions for signup")
        return {}


def _email_already_registered(email: str) -> bool:
    if not _is_valid_email(email):
        return False

    try:
        return _cached_profile_exists_for_email(email)
    except Exception as exc:
        raise SignupEmailCheckError("가입 여부를 확인하지 못했습니다. 잠시 후 다시 시도하세요.") from exc


def _should_show_resend_confirmation(email_registered: bool) -> bool:
    return email_registered or bool(st.session_state.get("signup_confirmation_email"))


def _is_existing_account_message(message: str) -> bool:
    return message.startswith(EXISTING_ACCOUNT_MESSAGE_PREFIX)


def _should_show_signup_login_link(email_registered: bool, email: str) -> bool:
    return email_registered or st.session_state.get("signup_existing_email") == email


__all__ = [
    "SignupEmailCheckError",
    "_cached_profile_exists_for_email",
    "_cached_required_policy_versions",
    "_email_already_registered",
    "_is_existing_account_message",
    "_is_valid_email",
    "_normalize_email",
    "_query_value",
    "_render_auth_card_header",
    "_render_email_feedback",
    "_render_login_secondary_actions",
    "_render_password_confirm_feedback",
    "_render_password_feedback",
    "_render_password_reset_form",
    "_render_password_update_form",
    "_render_signup_login_link",
    "_resend_cooldown_remaining",
    "_should_show_resend_confirmation",
    "_should_show_signup_login_link",
    "_signup_missing_required_fields",
    "_signup_required_policies",
    "render_login",
    "render_signup",
]
