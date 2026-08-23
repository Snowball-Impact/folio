from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ReferencePlatform:
    key: str
    label: str
    aliases: tuple[str, ...]
    url_markers: tuple[str, ...]
    description: str


REFERENCE_PLATFORMS = (
    ReferencePlatform(
        key="tableau",
        label="Tableau",
        aliases=("Tableau", "Viz Gallery"),
        url_markers=("tableau.com", "public.tableau.com"),
        description="Tableau Public과 Viz Gallery에서 수집한 인터랙티브 시각화 레퍼런스입니다.",
    ),
    ReferencePlatform(
        key="powerbi",
        label="Power BI",
        aliases=("PowerBI", "Power BI", "powerbi", "PBI"),
        url_markers=("app.powerbi.com", "powerbi.com"),
        description="Power BI 공개 보고서와 대시보드 레퍼런스입니다.",
    ),
    ReferencePlatform(
        key="datastudio",
        label="Data Studio",
        aliases=("Looker Studio", "Data Studio Gallery"),
        url_markers=("datastudio.google.com", "lookerstudio.google.com"),
        description="Looker Studio/Data Studio Gallery에서 수집한 보고서 레퍼런스입니다.",
    ),
    ReferencePlatform(
        key="streamlit",
        label="Streamlit",
        aliases=("Streamlit",),
        url_markers=("streamlit.app", "streamlit.io/gallery", "share.streamlit.io"),
        description="Streamlit 공식 갤러리에서 수집한 앱 레퍼런스입니다.",
    ),
)
REFERENCE_PLATFORM_BY_KEY = {platform.key: platform for platform in REFERENCE_PLATFORMS}
VISIBLE_REFERENCE_PLATFORM_KEYS = ("powerbi",)
VISIBLE_REFERENCE_PLATFORMS = tuple(
    platform for platform in REFERENCE_PLATFORMS if platform.key in VISIBLE_REFERENCE_PLATFORM_KEYS
)
DEFAULT_REFERENCE_PLATFORM_KEY = "powerbi"


def is_visible_reference_platform(platform_key: str) -> bool:
    return platform_key in VISIBLE_REFERENCE_PLATFORM_KEYS


def reference_platform_for_project(project: dict) -> str | None:
    tags = _normalized_values(project.get("tags") or [])
    url_text = " ".join(
        str(project.get(key) or "").lower()
        for key in ("power_bi_url", "report_url", "github_url", "thumbnail_url")
    )

    for platform in REFERENCE_PLATFORMS:
        platform_names = (platform.label, *platform.aliases)
        if any(name.lower() in tags for name in platform_names):
            return platform.key
        if any(marker.lower() in url_text for marker in platform.url_markers):
            return platform.key
    return None


def is_reference_project(project: dict) -> bool:
    return reference_platform_for_project(project) is not None


def reference_projects_for_platform(projects: Iterable[dict], platform_key: str) -> list[dict]:
    return [
        project
        for project in projects
        if reference_platform_for_project(project) == platform_key
    ]


def non_reference_projects(projects: Iterable[dict]) -> list[dict]:
    return [project for project in projects if not is_reference_project(project)]


def _normalized_values(values: Iterable[object]) -> set[str]:
    return {str(value).strip().lower() for value in values if str(value).strip()}
