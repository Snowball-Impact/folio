from __future__ import annotations

import logging
from typing import Any

from postgrest.types import CountMethod, ReturnMethod

from folio_app.services.project_normalizers import clean_project_payload
from folio_app.services.project_queries import _fetch_like_counts, _fetch_public_projects, clear_project_caches
from folio_app.services.project_types import ProjectResult, ViewCountResult
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


def create_project(author_id: str, payload: dict[str, Any]) -> ProjectResult:
    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    data = clean_project_payload(payload)
    data["author_id"] = author_id

    try:
        response = client.table("projects").insert(data).execute()
        if not response.data:
            return ProjectResult(False, "프로젝트 등록 응답을 확인할 수 없습니다.")
        clear_project_caches()
        return ProjectResult(True, "프로젝트가 등록되었습니다.", response.data[0]["id"])
    except Exception:
        logger.exception("Failed to create project")
        return ProjectResult(False, "프로젝트 등록에 실패했습니다. 잠시 후 다시 시도하세요.")


def update_project(project_id: str, author_id: str, payload: dict[str, Any]) -> ProjectResult:
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
        clear_project_caches()
        return ProjectResult(True, "프로젝트가 수정되었습니다.", project_id)
    except Exception as exc:
        if "42501" in str(exc) or "row-level security" in str(exc).lower():
            logger.exception("Project update was rejected by the remote RLS policy")
            return ProjectResult(
                False,
                "프로젝트 접근 정책이 최신 상태가 아닙니다. 관리자에게 Supabase RLS 정책 확인을 요청하세요.",
            )
        logger.exception("Failed to update project")
        return ProjectResult(False, "프로젝트 수정에 실패했습니다. 잠시 후 다시 시도하세요.")


def delete_project(project_id: str, author_id: str) -> ProjectResult:
    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    try:
        response = (
            client.table("projects")
            .delete()
            .eq("id", project_id)
            .eq("author_id", author_id)
            .execute()
        )
        if not response.data:
            return ProjectResult(False, "삭제할 프로젝트를 찾을 수 없습니다.")
        clear_project_caches()
        return ProjectResult(True, "프로젝트가 삭제되었습니다.", project_id)
    except Exception:
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

