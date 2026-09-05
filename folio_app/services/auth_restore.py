import logging

from folio_app.services.auth_account import apply_pending_policy_consents
from folio_app.services.auth_errors import friendly_auth_error
from folio_app.services.auth_session import save_auth_session
from folio_app.services.auth_types import AuthResult
from folio_app.services.profiles import ensure_profile
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


def restore_session(access_token: str, refresh_token: str) -> AuthResult:
    client = get_supabase_client()
    if client is None:
        return AuthResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        response = client.auth.set_session(access_token, refresh_token)
        if response.user is None or response.session is None:
            return AuthResult(False, "저장된 로그인 정보를 복원하지 못했습니다. 다시 로그인하세요.")

        save_auth_session(response.session, response.user.model_dump())

        metadata = response.user.user_metadata or {}
        try:
            ensure_profile(
                response.user.id,
                response.user.email or "",
                metadata.get("name", ""),
                metadata.get("organization", ""),
            )
        except Exception:
            # A valid auth session must survive an auxiliary profile repair failure.
            logger.exception("Session restored but profile repair failed")
        try:
            apply_pending_policy_consents(response.user.id, metadata.get("consented_policy_version_ids") or [])
        except Exception:
            # Consent backfill is also auxiliary; it must not discard auth state.
            logger.exception("Session restored but policy consent backfill failed")
        return AuthResult(True, "로그인 상태를 복원했습니다.")
    except Exception as exc:
        logger.warning("Session restore failed at auth binding: %s", type(exc).__name__)
        return AuthResult(False, friendly_auth_error("로그인 복원", exc))
