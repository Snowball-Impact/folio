from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import logging
from typing import Any

import streamlit as st

from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CommentResult:
    ok: bool
    message: str
    comment: dict[str, Any] | None = None
    comment_id: str | None = None


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
        return _attach_comment_authors(response.data or [])
    except Exception:
        logger.exception("Failed to list project comments")
        return []


def create_comment(project_id: str, author_id: str, body: str, parent_id: str | None = None) -> CommentResult:
    from folio_app.services.auth import ensure_authenticated_session

    normalized_body = body.strip()
    if not normalized_body:
        return CommentResult(False, "댓글 내용을 입력하세요.")
    if len(normalized_body) > 1000:
        return CommentResult(False, "댓글은 1,000자 이내로 입력하세요.")

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return CommentResult(False, auth_result.message)

    client = get_supabase_client()
    if client is None:
        return CommentResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    if parent_id and not _can_reply_to_comment(project_id, parent_id):
        return CommentResult(False, "답글을 남길 댓글을 확인할 수 없습니다.")

    payload = {
        "project_id": project_id,
        "author_id": author_id,
        "body": normalized_body,
        "parent_id": parent_id,
        "depth": 1 if parent_id else 0,
    }

    try:
        response = (
            client.table("comments")
            .insert(payload)
            .select("*")
            .execute()
        )
        if not response.data:
            return CommentResult(False, "댓글 등록에 실패했습니다.")
    except Exception:
        logger.exception("Failed to create project comment")
        return CommentResult(False, "댓글 등록에 실패했습니다. 잠시 후 다시 시도하세요.")

    clear_comment_caches()
    created = _attach_comment_authors(response.data or [])
    return CommentResult(True, "댓글이 등록되었습니다.", comment=created[0] if created else response.data[0])


def delete_comment(comment_id: str, author_id: str) -> CommentResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return CommentResult(False, auth_result.message)

    client = get_supabase_client()
    if client is None:
        return CommentResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        response = (
            client.table("comments")
            .delete()
            .eq("id", comment_id)
            .eq("author_id", author_id)
            .execute()
        )
        if not response.data:
            return CommentResult(False, "삭제할 댓글을 찾을 수 없습니다.")
    except Exception:
        logger.exception("Failed to delete project comment")
        return CommentResult(False, "댓글 삭제에 실패했습니다. 잠시 후 다시 시도하세요.")

    clear_comment_caches()
    return CommentResult(True, "댓글이 삭제되었습니다.", comment_id=comment_id)


def build_comment_tree(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row["id"]: {**row, "children": []} for row in rows}
    roots: list[dict[str, Any]] = []

    for row in rows:
        node = by_id[row["id"]]
        parent_id = row.get("parent_id")
        if parent_id and parent_id in by_id:
            by_id[parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


def count_comments_by_project(project_ids: list[str]) -> dict[str, int]:
    return _fetch_comment_counts(tuple(sorted(set(project_ids))))


@st.cache_data(ttl=15, show_spinner=False)
def _fetch_comment_counts(project_ids: tuple[str, ...]) -> dict[str, int]:
    client = get_supabase_client()
    if not project_ids:
        return {}
    if client is None:
        return {}

    try:
        response = (
            client.table("comments")
            .select("project_id")
            .in_("project_id", list(project_ids))
            .execute()
        )
    except Exception:
        logger.exception("Failed to count project comments")
        return {}

    counter: Counter[str] = Counter()
    for comment in response.data or []:
        project_id = comment.get("project_id")
        if project_id:
            counter[project_id] += 1
    return dict(counter)


def clear_comment_caches() -> None:
    _fetch_comment_counts.clear()


def _can_reply_to_comment(project_id: str, parent_id: str) -> bool:
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


def _attach_comment_authors(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
