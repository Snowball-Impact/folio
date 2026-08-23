from __future__ import annotations

import logging
from typing import Any

from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


def list_project_comments(project_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return []

    try:
        response = (
            client.table("comments")
            .select("*")
            .eq("project_id", project_id)
            .order("created_at", desc=False)
            .execute()
        )
        return attach_comment_authors(response.data or [])
    except Exception:
        logger.exception("Failed to list project comments")
        return []


def list_community_comments(post_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return []

    try:
        response = (
            client.table("comments")
            .select("*")
            .eq("community_post_id", post_id)
            .order("created_at", desc=False)
            .execute()
        )
        return attach_comment_authors(response.data or [])
    except Exception:
        logger.exception("Failed to list community comments")
        return []


def can_reply_to_comment(project_id: str, parent_id: str) -> bool:
    client = get_supabase_client()
    if client is None:
        return False

    try:
        response = (
            client.table("comments")
            .select("id, project_id, parent_id, depth")
            .eq("id", parent_id)
            .limit(1)
            .execute()
        )
    except Exception:
        logger.exception("Failed to validate reply target")
        return False

    parent = (response.data or [None])[0]
    if not parent:
        return False
    return (
        parent.get("project_id") == project_id
        and parent.get("parent_id") is None
        and (parent.get("depth") or 0) == 0
    )


def can_reply_to_community_comment(post_id: str, parent_id: str) -> bool:
    client = get_supabase_client()
    if client is None:
        return False

    try:
        response = (
            client.table("comments")
            .select("id, community_post_id, parent_id, depth")
            .eq("id", parent_id)
            .limit(1)
            .execute()
        )
    except Exception:
        logger.exception("Failed to validate community reply target")
        return False

    parent = (response.data or [None])[0]
    if not parent:
        return False
    return (
        parent.get("community_post_id") == post_id
        and parent.get("parent_id") is None
        and (parent.get("depth") or 0) == 0
    )


def attach_comment_authors(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not comments:
        return []

    client = get_supabase_client()
    if client is None:
        return comments

    author_ids = sorted({comment["author_id"] for comment in comments if comment.get("author_id")})
    profiles_by_id: dict[str, dict[str, Any]] = {}
    if author_ids:
        try:
            response = (
                client.table("public_profiles")
                .select("id, name")
                .in_("id", author_ids)
                .execute()
            )
            profiles_by_id = {profile["id"]: profile for profile in response.data or []}
        except Exception:
            logger.exception("Failed to attach comment authors")

    return [
        {
            **comment,
            "author": profiles_by_id.get(comment.get("author_id"), {}),
        }
        for comment in comments
    ]
