from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Callable

from postgrest.types import CountMethod, ReturnMethod

from folio_app.services.project_normalizers import (
    PROJECT_STATUS_DELETED,
    THUMBNAIL_MODE_CAPTURE,
    clean_project_payload,
)
from folio_app.services.project_thumbnails import maybe_capture_project_thumbnail, try_delete_project_thumbnail_file
from folio_app.services.project_queries import _fetch_like_counts, _fetch_public_projects, clear_project_caches
from folio_app.services.project_types import ProjectResult, ViewCountResult
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


ProgressCallback = Callable[[int, str], None]


def create_project(
    author_id: str,
    payload: dict[str, Any],
    progress_callback: ProgressCallback | None = None,
) -> ProjectResult:
    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    data = clean_project_payload(payload)
    data["author_id"] = author_id

    try:
        response = client.table("projects").insert(data).execute()
        if not response.data:
            return ProjectResult(False, "프로젝트 등록 응답을 확인할 수 없습니다.")
        project_id = response.data[0]["id"]
        capture_result = maybe_capture_project_thumbnail(project_id, data, progress_callback=progress_callback)
        clear_project_caches()
        return ProjectResult(True, _message_with_thumbnail_result("프로젝트가 등록되었습니다.", capture_result), project_id)
    except Exception as exc:
        if _is_thumbnail_mode_schema_error(exc):
            logger.exception("Project create failed because thumbnail_mode schema is missing")
            return ProjectResult(False, _thumbnail_mode_schema_message())
        logger.exception("Failed to create project")
        return ProjectResult(False, "프로젝트 등록에 실패했습니다. 잠시 후 다시 시도하세요.")


def update_project(
    project_id: str,
    author_id: str,
    payload: dict[str, Any],
    progress_callback: ProgressCallback | None = None,
) -> ProjectResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return ProjectResult(False, auth_result.message)

    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    data = clean_project_payload(payload)

    try:
        response = (
            client.table("projects")
            .update(data, count=CountMethod.exact, returning=ReturnMethod.minimal)
            .eq("id", project_id)
            .eq("author_id", author_id)
            .execute()
        )
        if response.count == 0:
            return ProjectResult(False, "수정할 프로젝트를 찾을 수 없습니다.")
        capture_result = maybe_capture_project_thumbnail(project_id, data, progress_callback=progress_callback)
        if "thumbnail_mode" in data and data.get("thumbnail_mode") != THUMBNAIL_MODE_CAPTURE:
            try_delete_project_thumbnail_file(project_id)
        clear_project_caches()
        return ProjectResult(True, _message_with_thumbnail_result("프로젝트가 수정되었습니다.", capture_result), project_id)
    except Exception as exc:
        if _is_thumbnail_mode_schema_error(exc):
            logger.exception("Project update failed because thumbnail_mode schema is missing")
            return ProjectResult(False, _thumbnail_mode_schema_message())
        if "42501" in str(exc) or "row-level security" in str(exc).lower():
            logger.exception("Project update was rejected by the remote RLS policy")
            return ProjectResult(
                False,
                "프로젝트 접근 정책이 최신 상태가 아닙니다. 관리자에게 Supabase RLS 정책 확인을 요청하세요.",
            )
        logger.exception("Failed to update project")
        return ProjectResult(False, "프로젝트 수정에 실패했습니다. 잠시 후 다시 시도하세요.")


def delete_project(project_id: str, author_id: str) -> ProjectResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return ProjectResult(False, auth_result.message)

    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        response = (
            client.table("projects")
            .update(
                {
                    "status": PROJECT_STATUS_DELETED,
                    "deleted_at": datetime.now(UTC).isoformat(),
                    "is_public": False,
                },
                count=CountMethod.exact,
                returning=ReturnMethod.minimal,
            )
            .eq("id", project_id)
            .eq("author_id", author_id)
            .execute()
        )
        if response.count == 0:
            return ProjectResult(False, "삭제할 프로젝트를 찾을 수 없습니다.")
        clear_project_caches()
        return ProjectResult(True, "프로젝트가 삭제되었습니다.", project_id)
    except Exception as exc:
        if _is_status_schema_error(exc):
            logger.exception("Project soft delete failed because status schema is missing")
            return ProjectResult(False, "프로젝트 삭제를 적용하려면 Supabase projects.status 컬럼을 먼저 적용해야 합니다.")
        logger.exception("Failed to delete project")
        return ProjectResult(False, "프로젝트 삭제에 실패했습니다. 잠시 후 다시 시도하세요.")


def increment_view_count(project_id: str, anonymous_viewer_id: str) -> ViewCountResult:
    client = get_supabase_client()
    if client is None:
        return ViewCountResult(False, False)

    try:
        response = client.rpc(
            "increment_project_view_count",
            {
                "project_id_input": project_id,
                "anonymous_viewer_id_input": anonymous_viewer_id,
            },
        ).execute()
        counted = response.data is True
        if counted:
            _fetch_public_projects.clear()
        return ViewCountResult(True, counted)
    except Exception:
        logger.exception("Failed to increment project view count")
        return ViewCountResult(False, False)


def set_project_liked(project_id: str, user_id: str, liked: bool) -> ProjectResult:
    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        if liked:
            client.table("likes").insert(
                {
                    "project_id": project_id,
                    "user_id": user_id,
                }
            ).execute()
            _fetch_like_counts.clear()
            return ProjectResult(True, "좋아요를 눌렀습니다.", project_id)

        client.table("likes").delete().eq("project_id", project_id).eq("user_id", user_id).execute()
        _fetch_like_counts.clear()
        return ProjectResult(True, "좋아요를 취소했습니다.", project_id)
    except Exception as exc:
        if liked and "duplicate" in str(exc).lower():
            return ProjectResult(True, "이미 좋아요를 누른 프로젝트입니다.", project_id)
        logger.exception("Failed to update project like")
        return ProjectResult(False, "좋아요 처리에 실패했습니다. 잠시 후 다시 시도하세요.", project_id)


def _message_with_thumbnail_result(message: str, capture_result: object) -> str:
    if getattr(capture_result, "skipped", False):
        return message
    if getattr(capture_result, "ok", False):
        return f"{message} 썸네일 캡처도 완료되었습니다."
    return f"{message} 썸네일은 기본 커버로 표시됩니다."


def _is_thumbnail_mode_schema_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "thumbnail_mode" in message and (
        "column" in message
        or "schema cache" in message
        or "check constraint" in message
        or "projects_thumbnail_mode_check" in message
    )


def _is_status_schema_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "status" in message and ("column" in message or "schema cache" in message)


def _thumbnail_mode_schema_message() -> str:
    return "프로젝트 썸네일 설정을 저장하려면 Supabase projects.thumbnail_mode 스키마를 최신 상태로 적용해야 합니다."
