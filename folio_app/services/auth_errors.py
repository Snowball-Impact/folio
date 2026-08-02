import logging


logger = logging.getLogger(__name__)


def friendly_auth_error(action: str, exc: Exception) -> str:
    message = str(exc)
    normalized = message.lower()

    if "email rate limit exceeded" in normalized or "rate limit" in normalized or "over_email_send_rate_limit" in normalized:
        return "인증 메일 발송 요청이 잠시 제한되었습니다. 잠시 후 다시 시도하세요."
    if (
        "redirect" in normalized
        and (
            "not allowed" in normalized
            or "invalid" in normalized
            or "uri" in normalized
            or "url" in normalized
        )
    ):
        return "Supabase Redirect URLs에 현재 앱 주소가 허용되어 있지 않습니다. Authentication URL Configuration을 확인하세요."
    if "error sending" in normalized or "smtp" in normalized or "email provider" in normalized:
        return "인증 메일 발송 서버 설정에 문제가 있습니다. Supabase SMTP 또는 이메일 템플릿 설정을 확인하세요."
    if "invalid email" in normalized or "email address" in normalized:
        return "올바른 이메일 주소를 입력하세요."
    if "already registered" in normalized or "user already registered" in normalized:
        return "이미 가입된 이메일입니다. 로그인하거나 인증 메일을 확인하세요."
    if "email not confirmed" in normalized:
        return "이메일 인증이 아직 완료되지 않았습니다. 인증 메일을 확인하세요."
    if "invalid login credentials" in normalized:
        return "이메일 또는 비밀번호를 확인하세요."
    if "otp" in normalized or "token" in normalized or "expired" in normalized:
        return "비밀번호 재설정 링크가 만료되었거나 이미 사용되었습니다. 다시 요청하세요."
    if "same password" in normalized or "different from the old password" in normalized:
        return "기존 비밀번호와 다른 새 비밀번호를 입력하세요."
    if "password" in normalized and ("weak" in normalized or "short" in normalized or "length" in normalized):
        return "비밀번호 보안 조건을 만족하지 못했습니다. 더 긴 비밀번호를 입력하세요."
    if "refresh token" in normalized:
        return "저장된 로그인 정보가 만료되었습니다. 다시 로그인하세요."
    if (
        "getaddrinfo failed" in normalized
        or "connecterror" in normalized
        or "temporary failure in name resolution" in normalized
        or "name or service not known" in normalized
    ):
        return "Supabase 서버에 연결하지 못했습니다. .env의 SUPABASE_URL 또는 네트워크/DNS 상태를 확인하세요."

    logger.warning(
        "Authentication action failed: %s",
        action,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return f"{action}에 실패했습니다. 잠시 후 다시 시도하세요."

