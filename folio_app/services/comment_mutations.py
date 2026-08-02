from __future__ import annotations

import logging
from typing import Any

from folio_app.services.comment_queries import attach_comment_authors, can_reply_to_comment
from folio_app.services.comment_stats import clear_comment_caches
from folio_app.services.comment_types import CommentResult
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


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

    if parent_id and not can_reply_to_comment(project_id, parent_id):
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
    created = attach_comment_authors(response.data or [])
    created_comment = created[0] if created else response.data[0]
    create_comment_notification(project_id, created_comment, author_id)
    return CommentResult(True, "댓글이 등록되었습니다.", comment=created_comment)


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


def create_comment_notification(project_id: str, comment: dict[str, Any], author_id: str) -> None:
    try:
        from folio_app.services.notifications import create_project_comment_notification

        create_project_comment_notification(project_id, comment, author_id)
    except Exception:
        logger.exception("Failed to dispatch comment notification")

