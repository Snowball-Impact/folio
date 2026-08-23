from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import logging
from typing import Any

import streamlit as st

from folio_app.services.comments import clear_comment_caches, comment_stats_by_project, count_comments_by_project
from folio_app.services.project_normalizers import PROJECT_STATUS_DELETED, PROJECT_STATUS_PUBLISHED
from folio_app.services.project_types import ProjectServiceError
from folio_app.services.supabase_client import get_supabase_client, recover_from_expired_jwt


logger = logging.getLogger(__name__)

HOME_LIKED_PROJECT_SAMPLE_MULTIPLIER = 20
HOME_PROJECT_SNAPSHOT_RPC = "home_project_snapshot"
PROJECT_DETAIL_SNAPSHOT_RPC = "project_detail_snapshot"

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
PROJECT_DETAIL_COLUMNS = PUBLIC_PROJECT_LIST_COLUMNS


@dataclass(frozen=True)
class HomeProjectSnapshot:
    total_project_count: int
    popular_tags: list[str]
    recent_projects: list[dict[str, Any]]
    viewed_projects: list[dict[str, Any]]
    liked_projects: list[dict[str, Any]]


@dataclass(frozen=True)
class HomeTagSummary:
    total_project_count: int
    popular_tags: list[str]


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


def list_home_project_snapshot(limit: int = 6, tag_limit: int = 10, platform_key: str | None = None) -> HomeProjectSnapshot:
    try:
        snapshot = _fetch_home_project_snapshot_rpc(limit, tag_limit, platform_key or "")
        if snapshot is not None:
            return snapshot
    except Exception:
        logger.warning("Home project snapshot RPC failed; falling back to table queries", exc_info=True)

    return _list_home_project_snapshot_from_queries(limit=limit, tag_limit=tag_limit, platform_key=platform_key)


def _list_home_project_snapshot_from_queries(
    limit: int = 6,
    tag_limit: int = 10,
    platform_key: str | None = None,
) -> HomeProjectSnapshot:
    try:
        if platform_key:
            return _list_home_platform_project_snapshot_from_queries(
                platform_key=platform_key,
                limit=limit,
                tag_limit=tag_limit,
            )

        recent_rows = _fetch_home_project_rows("created_at", limit)
        viewed_rows = _fetch_home_project_rows("view_count", limit)
        liked_ids = _fetch_home_liked_project_ids(limit)
        liked_rows = _fetch_public_projects_by_ids(tuple(liked_ids))

        project_by_id = _attach_related_data(_unique_projects([*recent_rows, *viewed_rows, *liked_rows]))
        attached_by_id = {project["id"]: project for project in project_by_id if project.get("id")}
        recent_projects = [attached_by_id[project["id"]] for project in recent_rows if project.get("id") in attached_by_id]
        viewed_projects = [attached_by_id[project["id"]] for project in viewed_rows if project.get("id") in attached_by_id]
        liked_projects = [attached_by_id[project_id] for project_id in liked_ids if project_id in attached_by_id]

        tag_summary = home_tag_summary(tag_limit)

        return HomeProjectSnapshot(
            total_project_count=tag_summary.total_project_count,
            popular_tags=tag_summary.popular_tags,
            recent_projects=recent_projects[:limit],
            viewed_projects=viewed_projects[:limit],
            liked_projects=liked_projects[:limit],
        )
    except ProjectServiceError:
        raise
    except Exception as exc:
        logger.exception("Failed to load home project snapshot")
        raise ProjectServiceError("공개 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc


def _list_home_platform_project_snapshot_from_queries(
    *,
    platform_key: str,
    limit: int,
    tag_limit: int,
) -> HomeProjectSnapshot:
    recent_rows = _fetch_home_platform_project_rows(platform_key, "created_at", limit)
    viewed_rows = _fetch_home_platform_project_rows(platform_key, "view_count", limit)
    liked_ids = _fetch_home_liked_project_ids(limit)
    liked_rows = _fetch_public_projects_by_ids(tuple(liked_ids))

    from folio_app.services.project_references import reference_platform_for_project

    liked_rows = [
        project
        for project in liked_rows
        if reference_platform_for_project(project) == platform_key
    ]
    project_by_id = _attach_related_data(_unique_projects([*recent_rows, *viewed_rows, *liked_rows]))
    attached_by_id = {project["id"]: project for project in project_by_id if project.get("id")}
    recent_projects = [attached_by_id[project["id"]] for project in recent_rows if project.get("id") in attached_by_id]
    viewed_projects = [attached_by_id[project["id"]] for project in viewed_rows if project.get("id") in attached_by_id]
    liked_projects = [attached_by_id[project["id"]] for project in liked_rows if project.get("id") in attached_by_id]
    tag_summary = _fetch_home_platform_tag_summary(platform_key, tag_limit)

    return HomeProjectSnapshot(
        total_project_count=tag_summary.total_project_count,
        popular_tags=tag_summary.popular_tags,
        recent_projects=recent_projects[:limit],
        viewed_projects=viewed_projects[:limit],
        liked_projects=liked_projects[:limit],
    )


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_home_project_snapshot_rpc(limit: int, tag_limit: int, platform_key: str = "") -> HomeProjectSnapshot | None:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    params = {
        "p_limit": limit,
        "p_tag_limit": tag_limit,
        "p_like_sample_limit": max(limit * HOME_LIKED_PROJECT_SAMPLE_MULTIPLIER, limit),
    }
    if platform_key:
        params["p_platform_key"] = platform_key

    try:
        response = _execute_public_read(
            lambda: client.rpc(
                HOME_PROJECT_SNAPSHOT_RPC,
                params,
            ).execute()
        )
    except Exception as exc:
        if platform_key and _is_missing_home_snapshot_platform_param(exc):
            return None
        raise
    if response is None:
        return None
    if not response.data:
        return None
    return _home_snapshot_from_payload(response.data)


def _home_snapshot_from_payload(payload: dict[str, Any]) -> HomeProjectSnapshot:
    return HomeProjectSnapshot(
        total_project_count=int(payload.get("total_project_count") or 0),
        popular_tags=list(payload.get("popular_tags") or []),
        recent_projects=list(payload.get("recent_projects") or []),
        viewed_projects=list(payload.get("viewed_projects") or []),
        liked_projects=list(payload.get("liked_projects") or []),
    )


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
def _fetch_home_platform_project_rows(platform_key: str, order_column: str, limit: int) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    platform_filter = _platform_project_filter(platform_key)
    if not platform_filter:
        return []

    response = _execute_public_read(
        lambda: (
            client.table("projects")
            .select(PUBLIC_PROJECT_LIST_COLUMNS)
            .eq("is_public", True)
            .eq("status", PROJECT_STATUS_PUBLISHED)
            .or_(platform_filter)
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

    sample_limit = max(limit * HOME_LIKED_PROJECT_SAMPLE_MULTIPLIER, limit)
    response = _execute_public_read(
        lambda: (
            client.table("likes")
            .select("project_id")
            .order("created_at", desc=True)
            .limit(sample_limit)
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
    return [project_id for project_id, _ in counter.most_common(limit)]


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
    return home_tag_summary(limit).popular_tags


def home_tag_summary(limit: int = 10) -> HomeTagSummary:
    return _fetch_home_tag_summary(limit)


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_home_tag_summary(limit: int) -> HomeTagSummary:
    projects = _fetch_public_project_tags()
    counter: Counter[str] = Counter()
    for project in projects:
        counter.update(project.get("tags") or [])
    return HomeTagSummary(
        total_project_count=len(projects),
        popular_tags=[tag for tag, _ in counter.most_common(limit)],
    )


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


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_home_platform_tag_summary(platform_key: str, limit: int) -> HomeTagSummary:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    platform_filter = _platform_project_filter(platform_key)
    if not platform_filter:
        return HomeTagSummary(total_project_count=0, popular_tags=[])

    response = _execute_public_read(
        lambda: (
            client.table("projects")
            .select("tags")
            .eq("is_public", True)
            .eq("status", PROJECT_STATUS_PUBLISHED)
            .or_(platform_filter)
            .execute()
        )
    )
    if response is None:
        raise ProjectServiceError("인기 태그를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    projects = response.data or []
    counter: Counter[str] = Counter()
    for project in projects:
        counter.update(project.get("tags") or [])
    return HomeTagSummary(
        total_project_count=len(projects),
        popular_tags=[tag for tag, _ in counter.most_common(limit)],
    )


def _platform_project_filter(platform_key: str) -> str:
    if platform_key != "powerbi":
        return ""
    return ",".join(
        (
            "tags.cs.{Power BI}",
            "tags.cs.{PowerBI}",
            "tags.cs.{powerbi}",
            "tags.cs.{PBI}",
            "power_bi_url.ilike.%powerbi.com%",
            "report_url.ilike.%powerbi.com%",
            "github_url.ilike.%powerbi.com%",
            "thumbnail_url.ilike.%powerbi.com%",
        )
    )


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


def _is_missing_home_snapshot_platform_param(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "home_project_snapshot" in message
        and "p_platform_key" in message
        and ("could not find the function" in message or "schema cache" in message)
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
        project = _fetch_project_detail_snapshot_rpc(project_id)
        if project is not None:
            return None if _project_status(project) == PROJECT_STATUS_DELETED else project
    except Exception:
        logger.warning("Project detail snapshot RPC failed; falling back to table queries", exc_info=True)

    try:
        response = _execute_public_read(
            lambda: client.table("projects").select(PROJECT_DETAIL_COLUMNS).eq("id", project_id).maybe_single().execute()
        )
    except Exception as exc:
        logger.exception("Failed to load project detail")
        raise ProjectServiceError("프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    if response is None:
        raise ProjectServiceError("프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

    try:
        projects = _attach_project_detail_data([response.data] if response.data else [])
    except Exception as exc:
        logger.exception("Failed to attach project detail metadata")
        raise ProjectServiceError("프로젝트 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.") from exc
    projects = [project for project in projects if _project_status(project) != PROJECT_STATUS_DELETED]
    return projects[0] if projects else None


@st.cache_data(ttl=15, show_spinner=False)
def _fetch_project_detail_snapshot_rpc(project_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        raise ProjectServiceError("Supabase 연결 설정을 확인하세요.")

    response = _execute_public_read(
        lambda: client.rpc(
            PROJECT_DETAIL_SNAPSHOT_RPC,
            {"p_project_id": project_id},
        ).execute()
    )
    if response is None:
        return None
    if not response.data:
        return None
    return dict(response.data)


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


def _attach_project_detail_data(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
    comment_counts = count_comments_by_project(project_ids)
    for project in projects:
        project["author"] = profiles_by_id.get(project.get("author_id"), {})
        project["like_count"] = like_counts.get(project["id"], 0)
        project["comment_count"] = comment_counts.get(project["id"], 0)

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
    _fetch_home_project_snapshot_rpc.clear()
    _fetch_project_detail_snapshot_rpc.clear()
    _fetch_public_projects.clear()
    _fetch_home_project_rows.clear()
    _fetch_home_platform_project_rows.clear()
    _fetch_public_projects_by_ids.clear()
    _fetch_home_liked_project_ids.clear()
    _fetch_public_project_tags.clear()
    _fetch_home_tag_summary.clear()
    _fetch_home_platform_tag_summary.clear()
    _fetch_public_profiles.clear()
    _fetch_like_counts.clear()
    clear_comment_caches()
