from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import logging
from typing import Any

from postgrest.types import CountMethod
import streamlit as st

from folio_app.services.comments import clear_comment_caches, comment_stats_by_project
from folio_app.services.project_normalizers import PROJECT_STATUS_DELETED, PROJECT_STATUS_PUBLISHED
from folio_app.services.project_types import ProjectServiceError
from folio_app.services.supabase_client import get_supabase_client, recover_from_expired_jwt


logger = logging.getLogger(__name__)

PUBLIC_PROJECT_LIST_COLUMNS = ",".join(
    (
        "id",
        "author_id",
        "title",
        "one_liner",
        "problem",
        "dataset",
        "process",
        "insights",
        "tags",
        "thumbnail_url",
        "power_bi_url",
        "report_url",
        "github_url",
        "project_type",
        "status",
        "embed_status",
        "is_public",
        "view_count",
        "created_at",
        "updated_at",
    )
)


@dataclass(frozen=True)
class HomeProjectSnapshot:
    total_project_count: int
    popular_tags: list[str]
    recent_projects: list[dict[str, Any]]
    viewed_projects: list[dict[str, Any]]
    liked_projects: list[dict[str, Any]]


def list_public_projects(
    search: str = "",
    tag: str = "전체",
    sort: str = "최신순",
    limit: int | None = 50,
) -> list[dict[str, Any]]:
    try:
        projects = _attach_related_data(_fetch_public_projects(), sort=sort)
        projects = _filter_public_projects(projects, search=search, tag=tag)
    except ProjectServiceError:
        raise
    except Exception as exc:
        logger.exception("Failed to load public projects")
        raise ProjectServiceError("공개 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    if sort == "조회수순":
        projects.sort(key=lambda project: project.get("view_count", 0) or 0, reverse=True)
    if limit is None:
        return projects
    return projects[:limit]


def list_home_project_snapshot(limit: int = 6, tag_limit: int = 10) -> HomeProjectSnapshot:
    try:
        recent_rows = _fetch_home_project_rows("created_at", limit)
        viewed_rows = _fetch_home_project_rows("view_count", limit)
        liked_ids = _fetch_home_liked_project_ids(limit * 3)
        liked_rows = _fetch_public_projects_by_ids(tuple(liked_ids))

        project_by_id = _attach_related_data(_unique_projects([*recent_rows, *viewed_rows, *liked_rows]))
        attached_by_id = {project["id"]: project for project in project_by_id if project.get("id")}
        recent_projects = [attached_by_id[project["id"]] for project in recent_rows if project.get("id") in attached_by_id]
        viewed_projects = [attached_by_id[project["id"]] for project in viewed_rows if project.get("id") in attached_by_id]
        liked_projects = [attached_by_id[project_id] for project_id in liked_ids if project_id in attached_by_id]

        return HomeProjectSnapshot(
            total_project_count=_fetch_public_project_count(),
            popular_tags=list_home_popular_tags(tag_limit),
            recent_projects=recent_projects[:limit],
            viewed_projects=viewed_projects[:limit],
            liked_projects=liked_projects[:limit],
        )
    except ProjectServiceError:
        raise
    except Exception as exc:
        logger.exception("Failed to load home project snapshot")
        raise ProjectServiceError("공개 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc


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
                .select(PUBLIC_PROJECT_LIST_COLUMNS)
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


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_home_project_rows(order_column: str, limit: int) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    response = _execute_public_read(
        lambda: (
            client.table("projects")
            .select(PUBLIC_PROJECT_LIST_COLUMNS)
            .eq("is_public", True)
            .eq("status", PROJECT_STATUS_PUBLISHED)
            .order(order_column, desc=True)
            .range(0, max(limit - 1, 0))
            .execute()
        )
    )
    if response is None:
        raise ProjectServiceError("공개 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")
    return response.data or []


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_public_projects_by_ids(project_ids: tuple[str, ...]) -> list[dict[str, Any]]:
    if not project_ids:
        return []
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    response = _execute_public_read(
        lambda: (
            client.table("projects")
            .select(PUBLIC_PROJECT_LIST_COLUMNS)
            .eq("is_public", True)
            .eq("status", PROJECT_STATUS_PUBLISHED)
            .in_("id", list(project_ids))
            .execute()
        )
    )
    if response is None:
        raise ProjectServiceError("공개 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")
    return response.data or []


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_home_liked_project_ids(limit: int) -> list[str]:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    response = _execute_public_read(lambda: client.table("likes").select("project_id").execute())
    if response is None:
        raise ProjectServiceError("좋아요 통계를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    counter: Counter[str] = Counter()
    for like in response.data or []:
        project_id = like.get("project_id")
        if project_id:
            counter[project_id] += 1
    return [project_id for project_id, _ in counter.most_common(limit)]


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_public_project_count() -> int:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    response = _execute_public_read(
        lambda: (
            client.table("projects")
            .select("id", count=CountMethod.exact)
            .eq("is_public", True)
            .eq("status", PROJECT_STATUS_PUBLISHED)
            .range(0, 0)
            .execute()
        )
    )
    if response is None:
        raise ProjectServiceError("공개 프로젝트 수를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")
    return int(getattr(response, "count", None) or len(response.data or []))


def _filter_public_projects(
    projects: list[dict[str, Any]],
    search: str = "",
    tag: str = "전체",
) -> list[dict[str, Any]]:
    filtered = [
        dict(project)
        for project in projects
        if _project_status(project) == PROJECT_STATUS_PUBLISHED
    ]
    if search:
        filtered = [project for project in filtered if _project_matches_search(project, search)]
    if tag and tag != "전체":
        filtered = [project for project in filtered if tag in (project.get("tags") or [])]
    return filtered


def list_popular_tags(limit: int | None = 10) -> list[str]:
    counter: Counter[str] = Counter()
    for project in _fetch_public_projects():
        counter.update(project.get("tags") or [])

    ranked_tags = counter.most_common(limit) if limit is not None else counter.most_common()
    return [tag for tag, _ in ranked_tags]


def list_home_popular_tags(limit: int = 10) -> list[str]:
    counter: Counter[str] = Counter()
    for project in _fetch_public_project_tags():
        counter.update(project.get("tags") or [])
    return [tag for tag, _ in counter.most_common(limit)]


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_public_project_tags() -> list[dict[str, Any]]:
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
                .select("tags")
                .eq("is_public", True)
                .eq("status", PROJECT_STATUS_PUBLISHED)
                .range(start, start + page_size - 1)
                .execute()
            )
        )
        if response is None:
            raise ProjectServiceError("인기 태그를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")
        page = response.data or []
        projects.extend(page)
        if len(page) < page_size:
            break
        start += page_size
    return projects


def _execute_public_read(operation):
    try:
        return operation()
    except Exception as exc:
        if recover_from_expired_jwt(exc):
            try:
                return operation()
            except Exception:
                logger.exception("Public read failed after JWT recovery")
                return None
        if _is_public_read_connection_error(exc):
            logger.warning("Public read failed because of a connection error", exc_info=True)
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
        visible_projects = [
            project
            for project in response.data or []
            if _project_status(project) != PROJECT_STATUS_DELETED
        ]
        return _attach_related_data(visible_projects)
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
    projects = [project for project in projects if _project_status(project) != PROJECT_STATUS_DELETED]
    return projects[0] if projects else None


def _project_status(project: dict[str, Any]) -> str:
    return str(project.get("status") or PROJECT_STATUS_PUBLISHED)


def is_project_liked(project_id: str, user_id: str | None) -> bool:
    client = get_supabase_client()
    if not user_id:
        return False
    if client is None:
        raise ProjectServiceError("좋아요 상태를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    try:
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
    except Exception as exc:
        logger.exception("Failed to load current user's like state")
        raise ProjectServiceError("좋아요 상태를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    if response is None:
        raise ProjectServiceError("좋아요 상태를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    return bool(response.data)


def count_author_stats(projects: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "project_count": len(projects),
        "view_count": sum(project.get("view_count", 0) or 0 for project in projects),
    }


def _project_matches_search(project: dict[str, Any], search: str) -> bool:
    term = search.strip().lower()
    if not term:
        return True

    author = project.get("author") or {}
    fields = [
        project.get("title") or "",
        project.get("one_liner") or "",
        project.get("problem") or "",
        project.get("dataset") or "",
        project.get("process") or "",
        project.get("insights") or "",
        " ".join(project.get("tags") or []),
        author.get("name") or "",
        author.get("organization") or "",
        project.get("created_at") or "",
    ]
    return any(term in str(field).lower() for field in fields)


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

    project_ids = [project["id"] for project in projects if project.get("id")]
    like_counts = _count_likes_by_project(project_ids)
    comment_counts, latest_comment_times = comment_stats_by_project(project_ids)
    for project in projects:
        project["author"] = profiles_by_id.get(project.get("author_id"), {})
        project["like_count"] = like_counts.get(project["id"], 0)
        project["comment_count"] = comment_counts.get(project["id"], 0)
        project["latest_comment_at"] = latest_comment_times.get(project["id"])

    if sort == "좋아요순":
        projects.sort(key=lambda project: project.get("like_count", 0), reverse=True)

    return projects


def _unique_projects(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for project in projects:
        project_id = project.get("id")
        if not project_id or project_id in seen:
            continue
        seen.add(project_id)
        unique.append(project)
    return unique


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_public_profiles(author_ids: tuple[str, ...]) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if not author_ids:
        return []
    if client is None:
        raise ProjectServiceError("작성자 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")
    try:
        response = _execute_public_read(
            lambda: client.table("public_profiles").select("id, name, organization").in_("id", list(author_ids)).execute()
        )
    except Exception:
        try:
            response = _execute_public_read(
                lambda: client.table("profiles").select("id, name, organization").in_("id", list(author_ids)).execute()
            )
        except Exception as exc:
            logger.exception("Failed to load public project authors")
            raise ProjectServiceError("작성자 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    if response is None:
        raise ProjectServiceError("작성자 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")
    return response.data or []


def _count_likes_by_project(project_ids: list[str]) -> dict[str, int]:
    return _fetch_like_counts(tuple(sorted(set(project_ids))))


@st.cache_data(ttl=15, show_spinner=False)
def _fetch_like_counts(project_ids: tuple[str, ...]) -> dict[str, int]:
    client = get_supabase_client()
    if not project_ids:
        return {}
    if client is None:
        raise ProjectServiceError("좋아요 통계를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    response = _execute_public_read(
        lambda: (
            client.table("likes")
            .select("project_id")
            .in_("project_id", list(project_ids))
            .execute()
        )
    )
    if response is None:
        raise ProjectServiceError("좋아요 통계를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    counter: Counter[str] = Counter()
    for like in response.data or []:
        project_id = like.get("project_id")
        if project_id:
            counter[project_id] += 1
    return dict(counter)


def clear_project_caches() -> None:
    _fetch_public_projects.clear()
    _fetch_home_project_rows.clear()
    _fetch_public_projects_by_ids.clear()
    _fetch_home_liked_project_ids.clear()
    _fetch_public_project_count.clear()
    _fetch_public_project_tags.clear()
    _fetch_public_profiles.clear()
    _fetch_like_counts.clear()
    clear_comment_caches()
