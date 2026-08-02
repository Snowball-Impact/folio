from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import threading
from typing import Any

import streamlit as st

from folio_app.services.supabase_client import get_supabase_client, get_supabase_service_role_client


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NotificationResult:
    ok: bool
    message: str


def create_project_comment_notification(project_id: str, comment: dict[str, Any], actor_id: str) -> NotificationResult:
    client = get_supabase_service_role_client() or get_supabase_client()
    comment_id = comment.get("id")
    if client is None or not project_id or not comment_id or not actor_id:
        return NotificationResult(False, "알림을 만들 수 없습니다.")

    try:
        project_response = (
            client.table("projects")
            .select("id, title, author_id")
            .eq("id", project_id)
            .limit(1)
            .execute()
        )
    except Exception:
        logger.exception("Failed to load project for notification")
        return NotificationResult(False, "알림 대상 프로젝트를 확인하지 못했습니다.")

    project = (project_response.data or [None])[0]
    if not project:
        return NotificationResult(False, "알림 대상 프로젝트를 찾지 못했습니다.")

    recipient_id = project.get("author_id")
    if not recipient_id or recipient_id == actor_id:
        return NotificationResult(True, "알림을 만들 필요가 없습니다.")

    project_title = project.get("title") or "프로젝트"
    payload = {
        "user_id": recipient_id,
        "actor_id": actor_id,
        "project_id": project_id,
        "comment_id": comment_id,
        "type": "project_comment",
        "title": f"{project_title}에 새 댓글이 남겨졌습니다.",
        "body": comment.get("body") or "",
    }

    try:
        client.table("notifications").insert(payload).execute()
    except Exception as exc:
        if _is_unique_violation(exc):
            clear_notification_caches()
            return NotificationResult(True, "이미 생성된 알림입니다.")
        logger.exception("Failed to create project comment notification")
        return NotificationResult(False, "알림을 만들지 못했습니다.")

    _send_project_comment_email(project, recipient_id, comment, actor_id)
    clear_notification_caches()
    return NotificationResult(True, "알림이 생성되었습니다.")


def list_notifications(user_id: str, limit: int = 20) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None or not user_id:
        return []

    try:
        response = (
            client.table("notifications")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
    except Exception:
        logger.exception("Failed to list notifications")
        return []
    return response.data or []


def count_unread_notifications(user_id: str) -> int:
    return _count_unread_notifications(user_id)


@st.cache_data(ttl=15, show_spinner=False)
def _count_unread_notifications(user_id: str) -> int:
    client = get_supabase_client()
    if client is None or not user_id:
        return 0

    try:
        response = (
            client.table("notifications")
            .select("id")
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
        )
    except Exception:
        logger.exception("Failed to count unread notifications")
        return 0
    return len(response.data or [])


def mark_notification_read(notification_id: str, user_id: str) -> bool:
    client = get_supabase_client()
    if client is None or not notification_id or not user_id:
        return False

    try:
        (
            client.table("notifications")
            .update({"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", notification_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception:
        logger.exception("Failed to mark notification read")
        return False
    clear_notification_caches()
    return True


def mark_all_notifications_read(user_id: str) -> bool:
    client = get_supabase_client()
    if client is None or not user_id:
        return False

    try:
        (
            client.table("notifications")
            .update({"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()})
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
        )
    except Exception:
        logger.exception("Failed to mark notifications read")
        return False
    clear_notification_caches()
    return True


def mark_project_comment_notifications_read(project_id: str, user_id: str) -> bool:
    client = get_supabase_client()
    if client is None or not project_id or not user_id:
        return False

    try:
        (
            client.table("notifications")
            .update({"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()})
            .eq("user_id", user_id)
            .eq("project_id", project_id)
            .eq("type", "project_comment")
            .eq("is_read", False)
            .execute()
        )
    except Exception:
        logger.exception("Failed to mark project comment notifications read")
        return False
    clear_notification_caches()
    return True


def clear_notification_caches() -> None:
    _count_unread_notifications.clear()


def _is_unique_violation(exc: Exception) -> bool:
    message = str(exc).lower()
    return "23505" in message or "duplicate key" in message or "unique constraint" in message


def _send_project_comment_email(
    project: dict[str, Any],
    recipient_id: str,
    comment: dict[str, Any],
    actor_id: str,
) -> None:
    thread = threading.Thread(
        target=_send_project_comment_email_now,
        args=(dict(project), recipient_id, dict(comment), actor_id),
        daemon=True,
        name="folio-comment-email",
    )
    thread.start()


def _send_project_comment_email_now(
    project: dict[str, Any],
    recipient_id: str,
    comment: dict[str, Any],
    actor_id: str,
) -> None:
    try:
        from folio_app.services.email_notifications import send_project_comment_email

        send_project_comment_email(project, recipient_id, comment, actor_id)
    except Exception:
        logger.exception("Failed to dispatch project comment email")
