from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
import html
import logging
import smtplib
from typing import Any
from urllib.parse import urlencode

from supabase import create_client

from folio_app.config import Settings, get_settings


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailDeliveryResult:
    ok: bool
    message: str
    skipped: bool = False


def send_project_comment_email(
    project: dict[str, Any],
    recipient_id: str,
    comment: dict[str, Any],
    actor_id: str,
) -> EmailDeliveryResult:
    settings = get_settings()
    if not settings.is_email_notifications_configured:
        return EmailDeliveryResult(True, "이메일 알림 설정이 없어 발송을 건너뜁니다.", skipped=True)

    recipient = _load_profile(settings, recipient_id)
    if not recipient or not recipient.get("email"):
        return EmailDeliveryResult(False, "수신자 이메일을 찾지 못했습니다.")

    actor = _load_profile(settings, actor_id) or {}
    actor_name = actor.get("name") or "사용자"
    subject = f"[FOLIO] {project.get('title') or '프로젝트'}에 새 댓글이 남겨졌습니다."
    message = _build_comment_email_message(settings, recipient["email"], subject, project, comment, actor_name)

    try:
        _send_email(settings, message)
    except Exception:
        logger.exception("Failed to send project comment email")
        return EmailDeliveryResult(False, "이메일 알림 발송에 실패했습니다.")

    return EmailDeliveryResult(True, "이메일 알림을 발송했습니다.")


def _load_profile(settings: Settings, user_id: str) -> dict[str, Any] | None:
    if not user_id:
        return None
    try:
        client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        response = (
            client.table("profiles")
            .select("id, email, name")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
    except Exception:
        logger.exception("Failed to load profile for email notification")
        return None
    return (response.data or [None])[0]


def _build_comment_email_message(
    settings: Settings,
    recipient_email: str,
    subject: str,
    project: dict[str, Any],
    comment: dict[str, Any],
    actor_name: str,
) -> EmailMessage:
    project_title = project.get("title") or "프로젝트"
    project_url = _project_url(settings, project.get("id") or "")
    comment_body = str(comment.get("body") or "").strip()
    preview = comment_body[:240]

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = recipient_email
    message.set_content(
        "\n".join(
            [
                f"{project_title}에 새 댓글이 남겨졌습니다.",
                "",
                f"작성자: {actor_name}",
                f"댓글: {preview}",
                "",
                f"프로젝트 보기: {project_url}",
            ]
        )
    )
    message.add_alternative(
        f"""
        <p><strong>{html.escape(project_title)}</strong>에 새 댓글이 남겨졌습니다.</p>
        <p><strong>작성자</strong>: {html.escape(actor_name)}</p>
        <p>{html.escape(preview)}</p>
        <p><a href="{html.escape(project_url, quote=True)}">프로젝트 보기</a></p>
        """,
        subtype="html",
    )
    return message


def _project_url(settings: Settings, project_id: str) -> str:
    separator = "&" if "?" in settings.app_url else "?"
    return f"{settings.app_url}{separator}{urlencode({'page': 'Home', 'project_id': project_id})}"


def _send_email(settings: Settings, message: EmailMessage) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username or settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
