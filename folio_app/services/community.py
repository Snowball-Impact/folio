from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from folio_app.services.profiles import get_profile
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "notice": "공지",
    "question": "질문",
    "tip": "팁·노하우",
    "other": "기타",
}
USER_CATEGORY_KEYS = ("question", "tip", "other")
ADMIN_CATEGORY_KEYS = ("notice", "question", "tip", "other")


@dataclass(frozen=True)
class CommunityResult:
    ok: bool
    message: str
    post_id: str | None = None
    post: dict[str, Any] | None = None


@dataclass(frozen=True)
class CommunityViewResult:
    ok: bool
    counted: bool


def is_admin_user(user_id: str | None) -> bool:
    if not user_id:
        return False
    try:
        profile = get_profile(user_id)
    except Exception:
        return False
    return (profile or {}).get("role") == "admin"


def category_options_for_user(user_id: str | None) -> list[str]:
    return list(ADMIN_CATEGORY_KEYS if is_admin_user(user_id) else USER_CATEGORY_KEYS)


def list_community_posts(category: str | None = None) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return []

    try:
        query = (
            client.table("community_posts")
            .select("*")
            .is_("deleted_at", "null")
            .eq("is_hidden", False)
        )
        if category in CATEGORY_LABELS:
            query = query.eq("category", category)
        response = query.order("is_pinned", desc=True).order("created_at", desc=True).execute()
        posts = response.data or []
    except Exception:
        logger.exception("Failed to list community posts")
        return []

    return _attach_post_related_data(posts)


def get_community_post(post_id: str, user_id: str | None = None) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        return None

    try:
        query = client.table("community_posts").select("*").eq("id", post_id).limit(1)
        if not is_admin_user(user_id):
            query = query.is_("deleted_at", "null").eq("is_hidden", False)
        response = query.execute()
    except Exception:
        logger.exception("Failed to load community post")
        return None

    posts = _attach_post_related_data(response.data or [])
    return posts[0] if posts else None


def create_community_post(author_id: str, category: str, title: str, content: str, *, is_pinned: bool = False) -> CommunityResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return CommunityResult(False, auth_result.message)

    cleaned = _clean_post_input(author_id, category, title, content, is_pinned=is_pinned)
    if isinstance(cleaned, CommunityResult):
        return cleaned

    client = get_supabase_client()
    if client is None:
        return CommunityResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        response = client.table("community_posts").insert(cleaned).execute()
        if not response.data:
            return CommunityResult(False, "게시글 등록 응답을 확인할 수 없습니다.")
    except Exception:
        logger.exception("Failed to create community post")
        return CommunityResult(False, "게시글 등록에 실패했습니다. 잠시 후 다시 시도하세요.")

    post_id = response.data[0]["id"]
    return CommunityResult(True, "게시글이 등록되었습니다.", post_id=post_id, post=response.data[0])


def update_community_post(
    post_id: str,
    author_id: str,
    category: str,
    title: str,
    content: str,
    *,
    is_pinned: bool = False,
) -> CommunityResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return CommunityResult(False, auth_result.message)

    cleaned = _clean_post_input(author_id, category, title, content, is_pinned=is_pinned)
    if isinstance(cleaned, CommunityResult):
        return cleaned
    cleaned.pop("user_id", None)
    cleaned["updated_at"] = datetime.now(UTC).isoformat()

    client = get_supabase_client()
    if client is None:
        return CommunityResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        query = client.table("community_posts").update(cleaned).eq("id", post_id)
        if not is_admin_user(author_id):
            query = query.eq("user_id", author_id)
        response = query.execute()
        if not response.data:
            return CommunityResult(False, "수정할 게시글을 찾을 수 없습니다.")
    except Exception:
        logger.exception("Failed to update community post")
        return CommunityResult(False, "게시글 수정에 실패했습니다. 잠시 후 다시 시도하세요.")

    return CommunityResult(True, "게시글이 수정되었습니다.", post_id=post_id, post=response.data[0])


def delete_community_post(post_id: str, user_id: str) -> CommunityResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return CommunityResult(False, auth_result.message)

    client = get_supabase_client()
    if client is None:
        return CommunityResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        query = (
            client.table("community_posts")
            .update({"deleted_at": datetime.now(UTC).isoformat(), "updated_at": datetime.now(UTC).isoformat()})
            .eq("id", post_id)
        )
        if not is_admin_user(user_id):
            query = query.eq("user_id", user_id)
        response = query.execute()
        if not response.data:
            return CommunityResult(False, "삭제할 게시글을 찾을 수 없습니다.")
    except Exception:
        logger.exception("Failed to delete community post")
        return CommunityResult(False, "게시글 삭제에 실패했습니다. 잠시 후 다시 시도하세요.")

    return CommunityResult(True, "게시글이 삭제되었습니다.", post_id=post_id)


def increment_community_post_view_count(post_id: str, anonymous_viewer_id: str | None) -> CommunityViewResult:
    client = get_supabase_client()
    if client is None:
        return CommunityViewResult(False, False)

    viewer_id = _uuid_or_new(anonymous_viewer_id)
    try:
        response = client.rpc(
            "increment_community_post_view_count",
            {
                "post_id_input": post_id,
                "anonymous_viewer_id_input": viewer_id,
            },
        ).execute()
        return CommunityViewResult(True, response.data is True)
    except Exception:
        logger.exception("Failed to increment community post view count")
        return CommunityViewResult(False, False)


def _clean_post_input(author_id: str, category: str, title: str, content: str, *, is_pinned: bool) -> dict[str, Any] | CommunityResult:
    normalized_category = category if category in CATEGORY_LABELS else ""
    normalized_title = " ".join((title or "").strip().split())
    normalized_content = (content or "").strip()
    admin = is_admin_user(author_id)

    if normalized_category not in (ADMIN_CATEGORY_KEYS if admin else USER_CATEGORY_KEYS):
        return CommunityResult(False, "선택할 수 없는 카테고리입니다.")
    if not normalized_title:
        return CommunityResult(False, "제목을 입력하세요.")
    if len(normalized_title) > 120:
        return CommunityResult(False, "제목은 120자 이내로 입력하세요.")
    if not normalized_content:
        return CommunityResult(False, "내용을 입력하세요.")
    if len(normalized_content) > 5000:
        return CommunityResult(False, "내용은 5,000자 이내로 입력하세요.")

    return {
        "user_id": author_id,
        "category": normalized_category,
        "title": normalized_title,
        "content": normalized_content,
        "is_pinned": bool(is_pinned and admin),
    }


def _attach_post_related_data(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not posts:
        return []

    client = get_supabase_client()
    if client is None:
        return posts

    post_ids = [post["id"] for post in posts if post.get("id")]
    author_ids = sorted({post["user_id"] for post in posts if post.get("user_id")})
    comment_counts = _comment_counts_by_post(post_ids)
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
            logger.exception("Failed to attach community post authors")

    return [
        {
            **post,
            "author": profiles_by_id.get(post.get("user_id"), {}),
            "comment_count": comment_counts.get(post.get("id"), 0),
        }
        for post in posts
    ]


def _comment_counts_by_post(post_ids: list[str]) -> dict[str, int]:
    if not post_ids:
        return {}
    client = get_supabase_client()
    if client is None:
        return {}

    try:
        response = (
            client.table("comments")
            .select("community_post_id")
            .in_("community_post_id", post_ids)
            .execute()
        )
    except Exception:
        logger.exception("Failed to load community comment counts")
        return {}

    counts = {post_id: 0 for post_id in post_ids}
    for row in response.data or []:
        post_id = row.get("community_post_id")
        if post_id in counts:
            counts[post_id] += 1
    return counts


def _uuid_or_new(value: str | None) -> str:
    try:
        return str(UUID(str(value))) if value else str(uuid4())
    except (TypeError, ValueError, AttributeError):
        return str(uuid4())
