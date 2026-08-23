from collections import Counter
import html

import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.assets import static_image_src
from folio_app.components.home_gallery import render_count_up_script, render_project_rails
from folio_app.components.ui import clean_html
from folio_app.navigation import navigate
from folio_app.pages import project_detail
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    list_home_project_snapshot,
    list_public_projects,
)
from folio_app.services.project_references import (
    REFERENCE_PLATFORMS,
    reference_platform_for_project,
)

_HOME_PAGE = "Home"
_ALL_PLATFORM_FILTER = "all"
_OTHER_PLATFORM_FILTER = "other"
_HOME_RAIL_PROJECT_LIMIT = 6
_HOME_HERO_SLIDES = (
    {
        "eyebrow": "Project Portfolio Platform",
        "title_html": "AI 시대에는 <em>휴먼 인사이트</em>가 자산이다.",
        "body": "데이터, AI, 웹 앱 프로젝트를 기록하고 공유하세요.",
        "visual": "preview",
        "cta": "내 프로젝트 등록하기",
    },
    {
        "eyebrow": "Collective Insight",
        "title_html": "인사이트는 <em>공유할수록 깊어집니다.</em>",
        "body": "프로젝트를 공유하고, 댓글과 반응으로 더 나은 결과물로 발전시키세요.",
        "visual": "guide",
        "cta": "내 프로젝트 등록하기",
    },
    {
        "eyebrow": "Power BI 무료 웹 게시",
        "title_html": "Power BI 보고서를 <em>무료로 웹에 게시하세요.</em>",
        "body": "PBIX 파일을 간편하게 웹에 배포하고, 공유 가능한 포트폴리오 페이지를 만들 수 있습니다.",
        "break_body_at_comma": True,
        "visual": "powerbi",
        "cta": "PBIX 보고서 무료 게시하기",
    },
    {
        "eyebrow": "Snowball Impact Study Club",
        "title_html": "Power BI 데이터 시각화, <em>함께 공부해요.</em>",
        "body": "스노우볼 임팩트 스터디 클럽에서 보고서 디자인, DAX, 경영정보시각화 실기를 함께 준비합니다.",
        "visual": "study",
        "cta": "스터디 클럽 참여하기",
        "cta_url": "https://discord.gg/vKb9SKA3k",
        "cta_target": "_blank",
    },
)
_HOME_GUIDE_STEPS = (
    ("01", "공유", "결과물과 제작 맥락을 모두와 공유합니다."),
    ("02", "피드백", "댓글과 반응으로 새로운 관점을 발견합니다."),
    ("03", "발전", "다양한 관점이 모여 인사이트를 개선합니다."),
)


def render() -> None:
    notice = st.session_state.pop("home_notice", None)
    if notice:
        st.success(notice)

    project_id = st.query_params.get("project_id")
    if project_id:
        project_detail.render(project_id)
        return

    _render_hero()
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        _render_loading_panel()

    search = st.query_params.get("q", "")
    selected_tag = st.query_params.get("tag", "전체")
    selected_platforms = _selected_platform_filters()
    try:
        if _uses_default_home_scope(search, selected_tag, selected_platforms):
            snapshot = list_home_project_snapshot(limit=_HOME_RAIL_PROJECT_LIMIT, tag_limit=40)
            recent_projects = snapshot.recent_projects
            viewed_projects = snapshot.viewed_projects
            liked_projects = snapshot.liked_projects
            total_project_count = snapshot.total_project_count
            popular_tags = _filter_platform_tags(snapshot.popular_tags)
        else:
            all_projects = list_public_projects(sort="최신순", limit=None)
            platform_projects = _filter_projects_by_platforms(all_projects, selected_platforms)
            recent_projects = _filter_projects_by_query(platform_projects, search=search, tag=selected_tag)
            viewed_projects = sorted(
                recent_projects,
                key=lambda project: project.get("view_count", 0) or 0,
                reverse=True,
            )
            liked_projects = sorted(
                recent_projects,
                key=lambda project: project.get("like_count", 0) or 0,
                reverse=True,
            )
            total_project_count = len(platform_projects)
            popular_tags = _popular_tags_from_projects(platform_projects)
    except ProjectServiceError as exc:
        loading_placeholder.empty()
        st.error(str(exc))
        if st.button("다시 시도", key="retry_public_projects"):
            clear_project_caches()
            st.rerun()
        return
    loading_placeholder.empty()
    _render_browse_panel(total_project_count, popular_tags, selected_platforms)
    render_project_rails(
        _project_rail_specs(recent_projects, viewed_projects, liked_projects),
        home_page=_HOME_PAGE,
        extra_query_params=_current_gallery_query_params(selected_platforms),
    )


def render_loading_shell() -> None:
    _render_hero()
    _render_loading_panel()


def _render_loading_panel() -> None:
    st.markdown(
        clean_html("""
        <section class="folio-home-loading-panel" aria-label="홈 갤러리 로딩 중">
            <h1>휴먼 인사이트 프로젝트를 불러오고 있어요.</h1>
            <p>잠시만 기다리면 검색과 프로젝트 갤러리가 이어서 표시됩니다.</p>
            <div class="folio-home-loading-search"></div>
            <div class="folio-home-loading-tags">
                <span></span><span></span><span></span><span></span><span></span>
            </div>
            <div class="folio-home-loading-rail" aria-hidden="true">
                <strong></strong>
                <div>
                    <span></span><span></span><span></span>
                </div>
            </div>
        </section>
        """),
        unsafe_allow_html=True,
    )


def _uses_default_home_scope(search: str, selected_tag: str, selected_platforms: set[str]) -> bool:
    return (
        not search.strip()
        and (not selected_tag or selected_tag == "전체")
        and (not selected_platforms or _ALL_PLATFORM_FILTER in selected_platforms)
    )


def _project_rail_specs(
    recent_projects: list[dict],
    viewed_projects: list[dict],
    liked_projects: list[dict],
) -> list[tuple[str, str, list[dict]]]:
    return [
        ("recent", "새로 공개된 프로젝트를 먼저 살펴보세요.", recent_projects[:_HOME_RAIL_PROJECT_LIMIT]),
        ("views", "조회수가 높은 프로젝트를 빠르게 훑어보세요.", viewed_projects[:_HOME_RAIL_PROJECT_LIMIT]),
        ("likes", "좋아요를 많이 받은 프로젝트를 확인해보세요.", liked_projects[:_HOME_RAIL_PROJECT_LIMIT]),
    ]


def _popular_tags_from_projects(projects: list[dict], limit: int = 10) -> list[str]:
    excluded_tags = _platform_tag_exclusions()
    counter: Counter[str] = Counter()
    for project in projects:
        counter.update(
            tag
            for tag in project.get("tags") or []
            if _normalized_tag(tag) not in excluded_tags
        )
    return [tag for tag, _ in counter.most_common(limit)]


def _filter_platform_tags(tags: list[str], limit: int = 10) -> list[str]:
    excluded_tags = _platform_tag_exclusions()
    return [tag for tag in tags if _normalized_tag(tag) not in excluded_tags][:limit]


def _platform_tag_exclusions() -> set[str]:
    excluded = {_normalized_tag(label) for _, label in _platform_filter_options()}
    excluded.update({_normalized_tag("All"), _normalized_tag("Other")})
    excluded.update(
        _normalized_tag(tag)
        for tag in (
            "reference",
            "references",
            "레퍼런스",
            "참고",
        )
    )
    for platform in REFERENCE_PLATFORMS:
        excluded.add(_normalized_tag(platform.label))
        excluded.update(_normalized_tag(alias) for alias in platform.aliases)
    return {tag for tag in excluded if tag}


def _normalized_tag(value: object) -> str:
    return str(value).strip().lower().replace(" ", "")


def _platform_filter_options() -> list[tuple[str, str]]:
    return [
        (_ALL_PLATFORM_FILTER, "전체"),
        (_OTHER_PLATFORM_FILTER, "기타"),
        *((platform.key, platform.label) for platform in REFERENCE_PLATFORMS),
    ]


def _selected_platform_filters() -> set[str]:
    raw_value = st.query_params.get("platforms", _ALL_PLATFORM_FILTER)
    requested_keys = [value.strip() for value in raw_value.split(",") if value.strip()]
    valid_keys = [key for key, _ in _platform_filter_options()]
    selected = next((key for key in requested_keys if key in valid_keys), _ALL_PLATFORM_FILTER)
    if selected == _ALL_PLATFORM_FILTER:
        return {_ALL_PLATFORM_FILTER}
    return {selected}


def _platform_query_value(selected_platforms: set[str]) -> str | None:
    if not selected_platforms or _ALL_PLATFORM_FILTER in selected_platforms:
        return None
    ordered_keys = [key for key, _ in _platform_filter_options() if key in selected_platforms]
    return ",".join(ordered_keys)


def _current_gallery_query_params(selected_platforms: set[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    search = st.query_params.get("q", "").strip()
    tag = st.query_params.get("tag", "전체")
    platform_query = _platform_query_value(selected_platforms)
    if search:
        params["q"] = search
    if tag and tag != "전체":
        params["tag"] = tag
    if platform_query:
        params["platforms"] = platform_query
    return params


def _filter_projects_by_platforms(projects: list[dict], selected_platforms: set[str]) -> list[dict]:
    if not selected_platforms or _ALL_PLATFORM_FILTER in selected_platforms:
        return list(projects)

    filtered_projects: list[dict] = []
    for project in projects:
        platform_key = reference_platform_for_project(project) or _OTHER_PLATFORM_FILTER
        if platform_key in selected_platforms:
            filtered_projects.append(project)
    return filtered_projects


def _filter_projects_by_query(projects: list[dict], *, search: str, tag: str) -> list[dict]:
    filtered = list(projects)
    if search:
        filtered = [project for project in filtered if _project_matches_search(project, search)]
    if tag and tag != "전체":
        filtered = [project for project in filtered if tag in (project.get("tags") or [])]
    return filtered


def _project_matches_search(project: dict, search: str) -> bool:
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


def _render_hero() -> None:
    # Append a clone of the first slide so the last -> first transition keeps
    # moving in the same direction before snapping back to the real first slide.
    track_slides = (*_HOME_HERO_SLIDES, _HOME_HERO_SLIDES[0])
    slides_html = "".join(_hero_slide_html(slide) for slide in track_slides)
    st.markdown(
        clean_html(f"""
        <section class="folio-home-hero-shell">
            <div class="folio-home-hero-viewport">
                <div class="folio-home-hero-track">
                    {slides_html}
                </div>
            </div>
            <div class="folio-home-hero-dots" aria-hidden="true">
                {"".join("<span></span>" for _ in _HOME_HERO_SLIDES)}
            </div>
        </section>
        """),
        unsafe_allow_html=True,
    )


def _render_browse_panel(project_count: int, popular_tags: list[str], selected_platforms: set[str]) -> None:
    initial_search = st.query_params.get("q", "")
    initial_tag = st.query_params.get("tag", "전체")
    project_count_label = f"{project_count:,}"

    with st.container(border=False, key="folio_browse_panel"), st.form("browse_filters"):
        st.markdown(
            f"""
            <div class="folio-search-container">
                <div class="folio-search-heading">
                    <h1 class="folio-search-title">
                        <span class="folio-search-title-count" data-folio-count-up="{project_count}">{project_count_label}</span>개의
                        휴먼 인사이트 프로젝트가 FOLIO에 쌓이고 있어요.
                    </h1>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_count_up_script()

        search_col, submit_col = st.columns([5, 1])
        with search_col:
            search_input = st.text_input(
                "프로젝트 검색",
                value=initial_search,
                placeholder="프로젝트명, 태그, 작성자, 소속, 등록일로 검색",
                label_visibility="collapsed",
                key="browse_search",
            )
        with submit_col:
            submitted = st.form_submit_button("검색", type="primary", use_container_width=True)

        option_keys = [key for key, _ in _platform_filter_options()]
        option_labels = {key: label for key, label in _platform_filter_options()}
        selected_platform = next(iter(selected_platforms), _ALL_PLATFORM_FILTER)
        if selected_platform not in option_keys:
            selected_platform = _ALL_PLATFORM_FILTER
        with st.container(key="home_platform_filters"):
            submitted_platform = st.radio(
                "콘텐츠 유형",
                option_keys,
                index=option_keys.index(selected_platform),
                format_func=lambda key: option_labels[key],
                horizontal=True,
                label_visibility="collapsed",
                key="home_platform_filter",
            )

        tag_options = ["전체", *popular_tags]
        if initial_tag not in tag_options:
            initial_tag = "전체"
        tag_col, tag_label_col = st.columns([5, 1.1], gap="small", vertical_alignment="center")
        with tag_col:
            selected_tag = st.pills(
                "태그 필터",
                tag_options,
                default=initial_tag,
                label_visibility="collapsed",
            ) or "전체"
        with tag_label_col:
            st.markdown('<div class="folio-popular-tag-label">인기 태그 TOP10</div>', unsafe_allow_html=True)

        if submitted:
            if search_input.strip():
                track_event("search", {"search_term": search_input.strip()})
            navigate(
                _HOME_PAGE,
                q=search_input.strip(),
                tag=selected_tag if selected_tag != "전체" else None,
                platforms=_platform_query_value({submitted_platform}),
            )


def _hero_slide_html(slide: dict[str, str]) -> str:
    hero_class = "folio-home-hero"
    if slide["visual"] == "guide":
        hero_class += " folio-home-guide-hero"
    cta_url = slide.get("cta_url") or "?page=Submit"
    cta_target = slide.get("cta_target") or "_self"
    cta_rel = ' rel="noopener"' if cta_target == "_blank" else ""
    return clean_html(f"""
    <section class="{hero_class}">
        <div class="folio-home-copy">
            <div class="folio-home-eyebrow">{html.escape(slide["eyebrow"])}</div>
            <h1>{slide["title_html"]}</h1>
            <p>{_hero_body_html(slide)}</p>
            <div class="folio-home-actions">
                <a class="folio-home-primary-cta" href="{html.escape(cta_url, quote=True)}" target="{html.escape(cta_target, quote=True)}"{cta_rel}>{html.escape(slide.get("cta") or "내 프로젝트 등록하기")}</a>
            </div>
        </div>
        {_hero_visual_html(slide["visual"])}
    </section>
    """)


def _hero_body_html(slide: dict[str, str]) -> str:
    body = html.escape(slide["body"])
    if slide.get("break_body_at_comma"):
        return body.replace(", ", ",<br>", 1)
    return body


def _hero_visual_html(visual: str) -> str:
    if visual == "preview":
        hero_preview_src = static_image_src("hero-preview-home.jpg")
        return (
            '<div class="folio-hero-preview">'
            f'<img class="folio-hero-preview-image" src="{hero_preview_src}" '
            'alt="데이터 분석 대시보드와 인사이트 미리보기" />'
            "</div>"
        )
    if visual == "guide":
        steps_html = "".join(_hero_guide_step_html(*step) for step in _HOME_GUIDE_STEPS)
        return f'<div class="folio-home-guide-flow" aria-label="프로젝트 발전 단계">{steps_html}</div>'
    if visual == "powerbi":
        steps = (
            ("PBIX", "업로드", "보고서 파일을 올립니다."),
            ("WEB", "웹 배포", "브라우저에서 열 수 있게 게시합니다."),
            ("LINK", "공유", "포트폴리오 링크로 전달합니다."),
        )
        steps_html = "".join(_hero_guide_step_html(*step) for step in steps)
        return f'<div class="folio-home-guide-flow folio-home-powerbi-flow" aria-label="Power BI 웹 게시 단계">{steps_html}</div>'
    if visual == "study":
        steps = (
            ("01", "실습", "Power BI 과제"),
            ("02", "웹 배포 및 피드백", "동료 리뷰 반영"),
            ("03", "완성", "포트폴리오 정리"),
        )
        steps_html = "".join(_hero_guide_step_html(*step) for step in steps)
        return f'<div class="folio-home-guide-flow folio-home-study-flow" aria-label="Power BI 스터디 진행 단계">{steps_html}</div>'
    return ""


def _hero_guide_step_html(step_number: str, title: str, body: str) -> str:
    return clean_html(f"""
    <div class="folio-home-guide-step">
        <div class="folio-home-guide-node">{html.escape(step_number)}</div>
        <div class="folio-home-guide-card">
            <strong>{html.escape(title)}</strong>
            <p>{html.escape(body)}</p>
        </div>
    </div>
    """)

