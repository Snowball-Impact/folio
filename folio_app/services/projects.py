from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
import logging
from typing import Any
from urllib.parse import urlparse

import streamlit as st
from postgrest.types import CountMethod, ReturnMethod

from folio_app.services.project_content import sanitize_project_html
from folio_app.services.supabase_client import get_supabase_client, recover_from_expired_jwt


logger = logging.getLogger(__name__)


class ProjectServiceError(RuntimeError):
    """A project operation failed in a way the UI can safely report."""


@dataclass(frozen=True)
class ProjectResult:
    ok: bool
    message: str
    project_id: str | None = None


def create_project(author_id: str, payload: dict[str, Any]) -> ProjectResult:
    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    data = _clean_project_payload(payload)
    data["author_id"] = author_id

    try:
        response = client.table("projects").insert(data).execute()
        if not response.data:
            return ProjectResult(False, "프로젝트 등록 응답을 확인할 수 없습니다.")
        clear_project_caches()
        return ProjectResult(True, "프로젝트가 등록되었습니다.", response.data[0]["id"])
    except Exception as exc:
        return ProjectResult(False, f"프로젝트 등록에 실패했습니다. ({exc})")


def update_project(project_id: str, author_id: str, payload: dict[str, Any]) -> ProjectResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return ProjectResult(False, auth_result.message)

    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    data = _clean_project_payload(payload)

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
        return ProjectResult(False, f"프로젝트 수정에 실패했습니다. ({exc})")


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
    except Exception as exc:
        return ProjectResult(False, f"프로젝트 삭제에 실패했습니다. ({exc})")


def list_public_projects(
    search: str = "",
    tag: str = "전체",
    sort: str = "최신순",
    limit: int = 50,
) -> list[dict[str, Any]]:
    try:
        projects = _filter_public_projects(_fetch_public_projects(), search=search, tag=tag)
        projects = _attach_related_data(projects, sort=sort)
    except ProjectServiceError:
        raise
    except Exception as exc:
        logger.exception("Failed to load public projects")
        raise ProjectServiceError("공개 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    if sort == "조회수순":
        projects.sort(key=lambda project: project.get("view_count", 0) or 0, reverse=True)
    return projects[:limit]


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_public_projects() -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    projects: list[dict[str, Any]] = []
    page_size = 500
    start = 0
    while True:
        response = _execute_public_read(
            lambda start=start: (
                client.table("projects")
                .select("*")
                .eq("is_public", True)
                .order("created_at", desc=True)
                .range(start, start + page_size - 1)
                .execute()
            )
        )
        if response is None:
            raise ProjectServiceError("공개 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")
        page = response.data or []
        projects.extend(page)
        if len(page) < page_size:
            break
        start += page_size
    return projects


def _filter_public_projects(
    projects: list[dict[str, Any]],
    search: str = "",
    tag: str = "전체",
) -> list[dict[str, Any]]:
    filtered = [dict(project) for project in projects]
    if search:
        filtered = [project for project in filtered if _project_matches_search(project, search)]
    if tag and tag != "전체":
        filtered = [project for project in filtered if tag in (project.get("tags") or [])]
    return filtered


def list_popular_tags(limit: int = 8) -> list[str]:
    counter: Counter[str] = Counter()
    for project in _fetch_public_projects():
        counter.update(project.get("tags") or [])

    return [tag for tag, _ in counter.most_common(limit)]


def _execute_public_read(operation):
    try:
        return operation()
    except Exception as exc:
        if recover_from_expired_jwt(exc):
            try:
                return operation()
            except Exception:
                return None
        if _is_public_read_connection_error(exc):
            return None
        raise


def _is_public_read_connection_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        marker in message
        for marker in (
            "connecterror",
            "getaddrinfo failed",
            "name or service not known",
            "temporary failure in name resolution",
            "nodename nor servname provided",
        )
    )


def list_projects_by_author(author_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    try:
        response = (
            client.table("projects")
            .select("*")
            .eq("author_id", author_id)
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        logger.exception("Failed to load projects for the current author")
        raise ProjectServiceError("내 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    try:
        return _attach_related_data(response.data or [])
    except Exception as exc:
        logger.exception("Failed to attach project metadata for the current author")
        raise ProjectServiceError("내 프로젝트 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc


def get_project(project_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    try:
        response = _execute_public_read(
            lambda: client.table("projects").select("*").eq("id", project_id).maybe_single().execute()
        )
    except Exception as exc:
        logger.exception("Failed to load project detail")
        raise ProjectServiceError("프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    if response is None:
        raise ProjectServiceError("프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    try:
        projects = _attach_related_data([response.data] if response.data else [])
    except Exception as exc:
        logger.exception("Failed to attach project detail metadata")
        raise ProjectServiceError("프로젝트 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    return projects[0] if projects else None


def increment_view_count(project_id: str) -> bool:
    client = get_supabase_client()
    if client is None:
        return False

    try:
        client.rpc("increment_project_view_count", {"project_id_input": project_id}).execute()
        _fetch_public_projects.clear()
        return True
    except Exception:
        logger.exception("Failed to increment project view count")
        return False


def is_project_liked(project_id: str, user_id: str | None) -> bool:
    client = get_supabase_client()
    if client is None or not user_id:
        return False

    response = _execute_public_read(
        lambda: (
            client.table("likes")
            .select("project_id")
            .eq("project_id", project_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
    )
    if response is None:
        return False

    return bool(response.data)


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
        return ProjectResult(False, f"좋아요 처리에 실패했습니다. ({exc})", project_id)


def count_author_stats(projects: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "project_count": len(projects),
        "view_count": sum(project.get("view_count", 0) or 0 for project in projects),
    }


def _clean_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if "title" in payload:
        data["title"] = payload.get("title", "").strip()
    if "one_liner" in payload:
        data["one_liner"] = payload.get("one_liner", "").strip() or None
    if "problem" in payload:
        data["problem"] = sanitize_project_html(payload.get("problem"))
    if "dataset" in payload:
        data["dataset"] = sanitize_project_html(payload.get("dataset")) or None
    if "process" in payload:
        data["process"] = sanitize_project_html(payload.get("process")) or None
    if "insights" in payload:
        data["insights"] = sanitize_project_html(payload.get("insights"))
    if "power_bi_url" in payload:
        data["power_bi_url"] = normalize_power_bi_embed_url(payload.get("power_bi_url", ""))
    if "report_url" in payload:
        data["report_url"] = normalize_optional_url(payload.get("report_url", ""))
    if "github_url" in payload:
        data["github_url"] = normalize_optional_url(payload.get("github_url", ""))
    if "thumbnail_url" in payload:
        data["thumbnail_url"] = normalize_optional_url(payload.get("thumbnail_url", ""))
    if "tags" in payload:
        data["tags"] = _normalize_tags(payload.get("tags", ""))
    if "is_public" in payload:
        data["is_public"] = bool(payload.get("is_public"))
    return data


def _normalize_tags(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        raw_tags = value
    else:
        raw_tags = value.replace("#", "").split(",")

    tags = []
    for tag in raw_tags:
        normalized = str(tag).strip()
        if normalized and normalized not in tags:
            tags.append(normalized)
    return tags[:10]


def normalize_optional_url(value: str | None) -> str | None:
    raw_value = (value or "").strip()
    if not raw_value:
        return None

    parsed = urlparse(raw_value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return raw_value
    return None


def normalize_power_bi_embed_url(value: str | None) -> str | None:
    raw_value = (value or "").strip()
    if not raw_value:
        return None

    if raw_value.lower().startswith("<iframe"):
        parser = _IframeSrcParser()
        parser.feed(raw_value)
        raw_value = parser.src or raw_value

    parsed = urlparse(raw_value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return raw_value
    return None


def _project_matches_search(project: dict[str, Any], search: str) -> bool:
    term = search.strip().lower()
    if not term:
        return True

    fields = [
        project.get("title") or "",
        project.get("one_liner") or "",
        project.get("problem") or "",
        project.get("dataset") or "",
        project.get("process") or "",
        project.get("insights") or "",
        " ".join(project.get("tags") or []),
    ]
    return any(term in str(field).lower() for field in fields)


class _IframeSrcParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.src: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "iframe":
            return

        for name, value in attrs:
            if name.lower() == "src" and value:
                self.src = value.strip()
                return


def _attach_related_data(projects: list[dict[str, Any]], sort: str = "최신순") -> list[dict[str, Any]]:
    if not projects:
        return []

    client = get_supabase_client()
    if client is None:
        return projects

    author_ids = sorted({project["author_id"] for project in projects if project.get("author_id")})
    profiles_by_id: dict[str, dict[str, Any]] = {}
    if author_ids:
        profiles_by_id = {
            profile["id"]: profile
            for profile in _fetch_public_profiles(tuple(author_ids))
        }

    like_counts = _count_likes_by_project([project["id"] for project in projects if project.get("id")])
    for project in projects:
        project["author"] = profiles_by_id.get(project.get("author_id"), {})
        project["like_count"] = like_counts.get(project["id"], 0)

    if sort == "좋아요순":
        projects.sort(key=lambda project: project.get("like_count", 0), reverse=True)

    return projects


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_public_profiles(author_ids: tuple[str, ...]) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None or not author_ids:
        return []
    try:
        response = _execute_public_read(
            lambda: client.table("public_profiles").select("id, name, organization").in_("id", list(author_ids)).execute()
        )
    except Exception:
        response = _execute_public_read(
            lambda: client.table("profiles").select("id, name, organization").in_("id", list(author_ids)).execute()
        )
    return response.data or [] if response is not None else []


def _count_likes_by_project(project_ids: list[str]) -> dict[str, int]:
    return _fetch_like_counts(tuple(sorted(set(project_ids))))


@st.cache_data(ttl=15, show_spinner=False)
def _fetch_like_counts(project_ids: tuple[str, ...]) -> dict[str, int]:
    client = get_supabase_client()
    if client is None or not project_ids:
        return {}

    response = _execute_public_read(
        lambda: (
            client.table("likes")
            .select("project_id")
            .in_("project_id", list(project_ids))
            .execute()
        )
    )
    if response is None:
        return {}

    counter: Counter[str] = Counter()
    for like in response.data or []:
        project_id = like.get("project_id")
        if project_id:
            counter[project_id] += 1
    return dict(counter)


def clear_project_caches() -> None:
    _fetch_public_projects.clear()
    _fetch_public_profiles.clear()
    _fetch_like_counts.clear()
