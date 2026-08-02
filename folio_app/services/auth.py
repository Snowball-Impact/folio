import streamlit as st

from folio_app.config import get_settings
from folio_app.services.auth_account import (
    apply_pending_policy_consents as _apply_pending_policy_consents,
    resend_signup_confirmation,
    sign_in,
    sign_up,
    sign_up_response_indicates_existing_user as _sign_up_response_indicates_existing_user,
)
from folio_app.services.auth_errors import friendly_auth_error as _friendly_auth_error
from folio_app.services.auth_password_reset import (
    complete_password_reset,
    complete_password_reset_with_code,
    complete_password_reset_with_token_hash,
    request_password_reset,
    update_password_and_clear_session as _update_password_and_clear_session,
)
from folio_app.services.auth_restore import restore_session
from folio_app.services.auth_session import (
    SESSION_CLEAR_BROWSER_AUTH_KEY,
    SESSION_LOGOUT_IN_PROGRESS_KEY,
    SESSION_PASSWORD_RESET_REFRESH_TOKEN_KEY,
    SESSION_PASSWORD_RESET_TOKEN_KEY,
    SESSION_REFRESH_TOKEN_KEY,
    SESSION_TOKEN_KEY,
    SESSION_USER_KEY,
    auth_user_to_dict as _auth_user_to_dict,
    bind_auth_response as _bind_auth_response,
    bind_current_client_session as _bind_current_client_session,
    bind_password_reset_session as _bind_password_reset_session,
    ensure_authenticated_session,
    get_auth_tokens,
    get_current_user,
    get_password_reset_tokens,
    save_auth_session as _save_auth_session,
    should_clear_browser_auth,
    sign_out,
)
from folio_app.services.auth_types import AuthResult
from folio_app.services.profiles import profile_exists_for_email
from folio_app.services.supabase_client import clear_supabase_client, get_supabase_client


__all__ = [
    "AuthResult",
    "SESSION_CLEAR_BROWSER_AUTH_KEY",
    "SESSION_LOGOUT_IN_PROGRESS_KEY",
    "SESSION_PASSWORD_RESET_REFRESH_TOKEN_KEY",
    "SESSION_PASSWORD_RESET_TOKEN_KEY",
    "SESSION_REFRESH_TOKEN_KEY",
    "SESSION_TOKEN_KEY",
    "SESSION_USER_KEY",
    "_apply_pending_policy_consents",
    "_auth_user_to_dict",
    "_bind_auth_response",
    "_bind_current_client_session",
    "_bind_password_reset_session",
    "_friendly_auth_error",
    "_save_auth_session",
    "_sign_up_response_indicates_existing_user",
    "_update_password_and_clear_session",
    "clear_supabase_client",
    "complete_password_reset",
    "complete_password_reset_with_code",
    "complete_password_reset_with_token_hash",
    "ensure_authenticated_session",
    "get_auth_tokens",
    "get_current_user",
    "get_password_reset_tokens",
    "get_settings",
    "get_supabase_client",
    "profile_exists_for_email",
    "request_password_reset",
    "resend_signup_confirmation",
    "restore_session",
    "should_clear_browser_auth",
    "sign_in",
    "sign_out",
    "sign_up",
    "st",
]
