from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

import streamlit as st

from folio_app.services.comment_utils import parse_timestamp
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


def annotate_unread_comment_status(projects: list[dict[str, Any]], user_id: str) -> list[dict[str, Any]]:
    unread_project_ids = get_unread_comment_project_ids(projects, user_id)
    for project in projects:
        project["has_unread_comments"] = project.get("id") in unread_project_ids
    return projects


def get_unread_comment_project_ids(projects: list[dict[str, Any]], user_id: str) -> set[str]:
    client = get_supabase_client()
    project_ids = [project["id"] for project in projects if project.get("id")]
    if client is None or not project_ids or not user_id:
        return set()

    try:
        comments_response = (
            client.table("comments")
            .select("project_id, author_id, created_at")
            .in_("project_id", project_ids)
            .neq("author_id", user_id)
            .execute()
        )
        reads_response = (
            client.table("project_comment_reads")
            .select("project_id, last_read_at")
            .eq("user_id", user_id)
            .in_("project_id", project_ids)
            .execute()
        )
    except Exception:
        logger.exception("Failed to load unread comment state")
        st.session_state["portfolio_unread_comment_error"] = (
            "새 댓글 표시 상태를 확인하지 못했습니다. Supabase 스키마 적용 여부를 확인하세요."
        )
        return set()

    latest_external_comments: dict[str, datetime] = {}
    for comment in comments_response.data or []:
        project_id = comment.get("project_id")
        created_at = parse_timestamp(comment.get("created_at"))
        if not project_id or created_at is None:
            continue
        current = latest_external_comments.get(project_id)
        if current is None or created_at > current:
            latest_external_comments[project_id] = created_at

    reads_by_project = {
        read["project_id"]: parse_timestamp(read.get("last_read_at"))
        for read in reads_response.data or []
        if read.get("project_id")
    }

    unread_project_ids: set[str] = set()
    for project_id, latest_comment_at in latest_external_comments.items():
        last_read_at = reads_by_project.get(project_id)
        if last_read_at is None or latest_comment_at > last_read_at:
            unread_project_ids.add(project_id)
    return unread_project_ids


def mark_project_comments_read(project_id: str, user_id: str) -> bool:
    from folio_app.services.auth import ensure_authenticated_session

    if not project_id or not user_id:
        return False

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return False

    client = get_supabase_client()
    if client is None:
        return False

    now = datetime.now(timezone.utc).isoformat()
    try:
        (
            client.table("project_comment_reads")
            .upsert(
                {
                    "project_id": project_id,
                    "user_id": user_id,
                    "last_read_at": now,
                    "updated_at": now,
                },
                on_conflict="project_id,user_id",
            )
            .execute()
        )
    except Exception:
        logger.exception("Failed to mark project comments as read")
        return False
    return True

