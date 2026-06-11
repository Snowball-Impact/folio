from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse

from folio_app.services.supabase_client import get_supabase_client, recover_from_expired_jwt


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
        return ProjectResult(True, "프로젝트가 등록되었습니다.", response.data[0]["id"])
    except Exception as exc:
        return ProjectResult(False, f"프로젝트 등록에 실패했습니다. ({exc})")


def update_project(project_id: str, author_id: str, payload: dict[str, Any]) -> ProjectResult:
    client = get_supabase_client()
    if client is None:
        return ProjectResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    data = _clean_project_payload(payload)

    try:
        response = (
            client.table("projects")
            .update(data)
            .eq("id", project_id)
            .eq("author_id", author_id)
            .execute()
        )
        if not response.data:
            return ProjectResult(False, "수정할 프로젝트를 찾을 수 없습니다.")
        return ProjectResult(True, "프로젝트가 수정되었습니다.", project_id)
    except Exception as exc:
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
        return ProjectResult(True, "프로젝트가 삭제되었습니다.", project_id)
    except Exception as exc:
        return ProjectResult(False, f"프로젝트 삭제에 실패했습니다. ({exc})")


def list_public_projects(
    search: str = "",
    tag: str = "전체",
    sort: str = "최신순",
    limit: int = 50,
) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return []

    response = _execute_public_read(lambda: _build_public_projects_query(client, search, tag, sort, limit).execute())
    if response is None:
        return []

    projects = response.data or []
    if search:
        projects = [
            project for project in projects
            if _project_matches_search(project, search)
        ]
    if tag and tag != "전체":
        projects = [project for project in projects if tag in (project.get("tags") or [])]

    projects = _attach_related_data(projects, sort=sort)
    return projects[:limit]


def _build_public_projects_query(client, search: str, tag: str, sort: str, limit: int):
    query = client.table("projects").select("*").eq("is_public", True)

    if sort == "조회수순":
        query = query.order("view_count", desc=True)
    else:
        query = query.order("created_at", desc=True)

    needs_local_filtering = bool(search.strip()) or (tag and tag != "전체") or sort == "좋아요순"
    fetch_limit = max(limit, 250) if needs_local_filtering else limit
    return query.limit(max(fetch_limit, 1))


def list_popular_tags(limit: int = 8) -> list[str]:
    client = get_supabase_client()
    if client is None:
        return []

    response = _execute_public_read(
        lambda: client.table("projects").select("tags").eq("is_public", True).execute()
    )
    if response is None:
        return []

    counter: Counter[str] = Counter()
    for project in response.data or []:
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
        raise


def list_projects_by_author(author_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return []

    response = (
        client.table("projects")
        .select("*")
        .eq("author_id", author_id)
        .order("created_at", desc=True)
        .execute()
    )
    return _attach_related_data(response.data or [])


def get_project(project_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        return None

    response = _execute_public_read(
        lambda: client.table("projects").select("*").eq("id", project_id).single().execute()
    )
    if response is None:
        return None

    projects = _attach_related_data([response.data] if response.data else [])
    return projects[0] if projects else None


def increment_view_count(project_id: str) -> None:
    client = get_supabase_client()
    if client is None:
        return

    try:
        client.rpc("increment_project_view_count", {"project_id_input": project_id}).execute()
    except Exception:
        # The RPC is added in supabase/schema.sql. Ignore until the SQL is applied remotely.
        return


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
            return ProjectResult(True, "좋아요를 눌렀습니다.", project_id)

        client.table("likes").delete().eq("project_id", project_id).eq("user_id", user_id).execute()
        return ProjectResult(True, "좋아요를 취소했습니다.", project_id)
    except Exception as exc:
        if liked and "duplicate" in str(exc).lower():
            return ProjectResult(True, "이미 좋아요를 누른 프로젝트입니다.", project_id)
        return ProjectResult(False, f"좋아요 처리에 실패했습니다. ({exc})", project_id)


def count_author_stats(author_id: str) -> dict[str, int]:
    projects = list_projects_by_author(author_id)
    return {
        "project_count": len(projects),
        "view_count": sum(project.get("view_count", 0) or 0 for project in projects),
    }


def _clean_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": payload.get("title", "").strip(),
        "one_liner": payload.get("one_liner", "").strip() or None,
        "problem": payload.get("problem", "").strip(),
        "dataset": payload.get("dataset", "").strip() or None,
        "process": payload.get("process", "").strip() or None,
        "insights": payload.get("insights", "").strip(),
        "power_bi_url": normalize_power_bi_embed_url(payload.get("power_bi_url", "")),
        "report_url": normalize_optional_url(payload.get("report_url", "")),
        "github_url": normalize_optional_url(payload.get("github_url", "")),
        "thumbnail_url": normalize_optional_url(payload.get("thumbnail_url", "")),
        "ai_summary": payload.get("ai_summary", "").strip() or None,
        "tags": _normalize_tags(payload.get("tags", "")),
        "is_public": True,
    }


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
        project.get("ai_summary") or "",
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
        profiles = _execute_public_read(
            lambda: client.table("profiles").select("id, name, organization").in_("id", author_ids).execute()
        )
        if profiles is None:
            profiles_by_id = {}
        else:
            profiles_by_id = {profile["id"]: profile for profile in profiles.data or []}

    like_counts = _count_likes_by_project([project["id"] for project in projects if project.get("id")])
    for project in projects:
        project["author"] = profiles_by_id.get(project.get("author_id"), {})
        project["like_count"] = like_counts.get(project["id"], 0)

    if sort == "좋아요순":
        projects.sort(key=lambda project: project.get("like_count", 0), reverse=True)

    return projects


def _count_likes_by_project(project_ids: list[str]) -> dict[str, int]:
    client = get_supabase_client()
    if client is None or not project_ids:
        return {}

    response = _execute_public_read(
        lambda: (
            client.table("likes")
            .select("project_id")
            .in_("project_id", project_ids)
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
