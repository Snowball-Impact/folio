import html

import streamlit as st

from folio_app.components.layout import render_hero
from folio_app.components.project_form import (
    PROJECT_BODY_TEMPLATE,
    build_project_payload,
    project_body_from_project,
    render_project_form,
    validate_project_form,
)
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.profiles import get_profile, update_profile
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    count_author_stats,
    create_project,
    delete_project,
    list_projects_by_author,
    update_project,
)


def _render_login_required(page_key: str, message: str) -> None:
    st.warning(message)
    login_col, gallery_col = st.columns(2)
    with login_col:
        if st.button("로그인하기", key=f"login_required_{page_key}_login", use_container_width=True):
            navigate("Login")
    with gallery_col:
        if st.button("홈으로", key=f"login_required_{page_key}_home", use_container_width=True):
            navigate("Home")


def render_submit() -> None:
    user = get_current_user()
    render_hero(
        "Submit",
        "새 프로젝트 등록",
        "당신의 데이터 분석 프로젝트를 포트폴리오로 공개하세요.",
        image_name="hero-submit.png",
        image_alt="데이터 분석 프로젝트 등록 화면 일러스트",
    )

    if not user:
        _render_login_required("submit", "프로젝트를 등록하려면 로그인이 필요합니다.")
        return

    form_data, submitted, _ = render_project_form(
        "submit",
        title="",
        one_liner="",
        tags="",
        project_body_initial=PROJECT_BODY_TEMPLATE,
        power_bi_url="",
        github_url="",
        etc_url="",
        submit_label="프로젝트 등록하기",
    )

    if not submitted:
        return

    parsed_body, missing, url_error = validate_project_form(form_data)
    if missing:
        st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
        return
    if url_error:
        st.error(url_error)
        return

    result = create_project(
        user["id"],
        build_project_payload(form_data, parsed_body),
    )

    if result.ok:
        st.session_state["project_notice"] = result.message
        navigate("Home", project_id=result.project_id)
    else:
        st.error(result.message)


def render_my_portfolio() -> None:
    navigate("My Page")


def render_profile() -> None:
    navigate("My Page")


def render_my_page() -> None:
    user = get_current_user()
    editing_project_id = st.session_state.get("editing_project_id") if user else None

    render_hero(
        "My Page",
        "마이 페이지",
        "프로필과 포트폴리오를 한곳에서 관리하세요.",
        image_name="hero-my-page-v2.png",
        image_alt="프로필 카드와 포트폴리오 통계를 표현한 3D 일러스트",
    )

    if not user:
        _render_login_required("my_page", "마이 페이지를 이용하려면 로그인이 필요합니다.")
        return

    notice = st.session_state.pop("portfolio_notice", None)
    if notice:
        st.success(notice)

    try:
        projects = list_projects_by_author(user["id"])
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("다시 시도", key="retry_my_portfolio"):
            clear_project_caches()
            st.rerun()
        return

    if editing_project_id:
        project = next((item for item in projects if item["id"] == editing_project_id), None)
        if project:
            _render_edit_project_form(user["id"], project)
            return
        st.session_state.pop("editing_project_id", None)
        st.rerun()

    profile = get_profile(user["id"])
    if profile is None:
        st.info("프로필 정보를 불러오는 중 문제가 발생했습니다.")
        return

    if st.session_state.get("editing_profile"):
        _render_profile_edit_form(user["id"], profile)
        return

    _render_profile_view(user, profile, projects)


@st.dialog("프로젝트 삭제")
def _confirm_project_deletion(project: dict, author_id: str) -> None:
    title = project.get("title") or "제목 없는 프로젝트"
    st.write(f"‘{title}’ 프로젝트를 삭제할까요?")
    st.caption("삭제한 프로젝트는 복구할 수 없습니다.")

    cancel_col, delete_col = st.columns(2)
    with cancel_col:
        if st.button("취소", key=f"delete_cancel_{project['id']}", use_container_width=True):
            st.rerun()
    with delete_col:
        if st.button(
            "삭제하기",
            key=f"delete_confirm_{project['id']}",
            type="primary",
            use_container_width=True,
        ):
            result = delete_project(project["id"], author_id)
            if result.ok:
                st.session_state["portfolio_notice"] = result.message
                st.rerun()
            else:
                st.error(result.message)


def _render_profile_view(user: dict, profile: dict, projects: list[dict]) -> None:
    stats = count_author_stats(projects)
    public_count = sum(1 for project in projects if project.get("is_public"))
    like_count = sum(project.get("like_count", 0) or 0 for project in projects)

    name = profile.get("name") or user.get("email") or ""
    email = profile.get("email") or user.get("email") or ""
    organization = profile.get("organization") or ""
    bio = profile.get("bio") or ""

    organization_label = organization or "소속을 추가해 나를 더 잘 소개해 보세요"
    bio_label = bio or "아직 자기소개가 없습니다. 어떤 관점으로 데이터를 바라보는지 들려주세요."

    with st.container(border=True, key="profile_overview"):
        st.markdown(
            f"""
            <div class="folio-profile-identity">
                <div class="folio-profile-identity-copy">
                    <span class="folio-profile-kicker">MY PROFILE</span>
                    <dl class="folio-profile-fields">
                        <div>
                            <dt>작성자</dt>
                            <dd class="folio-profile-name">{html.escape(name)}</dd>
                        </div>
                        <div>
                            <dt>소속</dt>
                            <dd class="folio-profile-info-org{' is-empty' if not organization else ''}">{html.escape(organization_label)}</dd>
                        </div>
                        <div>
                            <dt>이메일</dt>
                            <dd class="folio-profile-email">{html.escape(email)}</dd>
                        </div>
                    </dl>
                </div>
            </div>
            <div class="folio-profile-about">
                <span>ABOUT</span>
                <p class="folio-profile-bio{' is-empty' if not bio else ''}">{html.escape(bio_label)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("전체 프로젝트", stats["project_count"])
        m2.metric("공개 프로젝트", public_count)
        m3.metric("누적 조회", f"{stats['view_count']:,}")
        m4.metric("총 좋아요", f"{like_count:,}")

        if st.button("프로필 편집", key="start_edit_profile", icon=":material/edit:"):
            st.session_state["editing_profile"] = True
            st.rerun()

    st.markdown(
        """
        <div class="folio-profile-section-heading">
            <div>
                <span>MY PORTFOLIO</span>
            </div>
            <p>등록한 프로젝트를 확인하고 수정하거나 삭제할 수 있습니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if projects:
        for project in projects:
            with st.container(border=True, key=f"portfolio_item_{project['id']}"):
                project_col, actions_col = st.columns([5, 1], gap="small")
                with project_col:
                    _render_portfolio_item(project)
                with actions_col:
                    if st.button("보기", key=f"portfolio_view_{project['id']}", use_container_width=True):
                        navigate("Home", project_id=project["id"])
                    if st.button("수정", key=f"portfolio_edit_{project['id']}", use_container_width=True):
                        st.session_state["editing_project_id"] = project["id"]
                        st.rerun()
                    if st.button("삭제", key=f"portfolio_delete_{project['id']}", use_container_width=True):
                        _confirm_project_deletion(project, user["id"])
    else:
        with st.container(border=False, key="profile_empty_projects"):
            st.markdown(
                """
                <div class="folio-profile-empty-icon">＋</div>
                <h3>첫 프로젝트를 포트폴리오에 담아보세요</h3>
                <p>분석 과정과 인사이트를 기록하면 이곳에 활동이 쌓입니다.</p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("프로젝트 등록하기", key="profile_create_project", type="primary"):
                navigate("Submit")
def _render_profile_edit_form(user_id: str, profile: dict) -> None:
    with st.container(border=True, key="profile_edit_card"):
        st.markdown(
            """
            <div class="folio-profile-edit-heading">
                <span>EDIT PROFILE</span>
                <h2>프로필 정보 수정</h2>
                <p>포트폴리오 방문자에게 보여줄 기본 정보를 관리합니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("profile_edit_form"):
            name = st.text_input("이름", value=profile.get("name") or "", placeholder="이름을 입력하세요")
            organization = st.text_input(
                "소속",
                value=profile.get("organization") or "",
                placeholder="학교, 기관 또는 회사",
            )
            bio = st.text_area(
                "자기소개",
                value=profile.get("bio") or "",
                height=150,
                placeholder="관심 분야와 데이터 분석 관점을 소개해 보세요.",
                max_chars=300,
            )
            st.caption("자기소개는 최대 300자까지 입력할 수 있습니다.")
            cancel_col, save_col = st.columns([1, 1.4])
            cancelled = cancel_col.form_submit_button("취소", use_container_width=True)
            submitted = save_col.form_submit_button("변경사항 저장", type="primary", use_container_width=True)

    if cancelled:
        st.session_state.pop("editing_profile", None)
        st.rerun()

    if not submitted:
        return

    name = name.strip()
    if not name:
        st.error("이름을 입력하세요.")
        return

    try:
        update_profile(user_id, name=name, organization=organization.strip(), bio=bio.strip())
    except Exception as exc:
        st.error(f"프로필 저장에 실패했습니다. ({exc})")
        return

    st.session_state.pop("editing_profile", None)
    st.success("프로필이 업데이트됐습니다.")
    st.rerun()


from folio_app.components.ui import render_tag_chips, render_project_metrics


def _render_portfolio_item(project: dict) -> None:
    title = html.escape(project.get("title") or "Untitled")
    one_liner = html.escape(project.get("one_liner") or "")
    tags_html = render_tag_chips(project.get("tags") or [])
    is_public = bool(project.get("is_public"))
    visibility_label = "공개" if is_public else "비공개"
    visibility_icon = (
        '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"></path></svg>'
        if is_public
        else '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"></rect><path d="M8 10V7a4 4 0 0 1 8 0v3"></path></svg>'
    )
    metrics_html = render_project_metrics(
        project,
        container_class="folio-portfolio-card-meta",
        extra_html=f"<span title=\"{visibility_label}\" aria-label=\"공개 상태 {visibility_label}\">{visibility_icon}</span>",
    )
    liner_html = f"<p class='folio-portfolio-card-liner'>{one_liner}</p>" if one_liner else ""

    st.markdown(
        f"""
        <div class="folio-portfolio-card">
            <div class="folio-portfolio-card-main">
                <p class="folio-portfolio-card-title">{title}</p>
                {liner_html}
            </div>
            <div class="folio-portfolio-card-footer">
                {tags_html}
                {metrics_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_edit_project_form(author_id: str, project: dict) -> None:
    st.markdown("### 프로젝트 수정")

    form_data, submitted, cancelled = render_project_form(
        f"edit_{project['id']}",
        title=project.get("title") or "",
        one_liner=project.get("one_liner") or "",
        tags=", ".join(project.get("tags") or []),
        project_body_initial=project_body_from_project(project),
        power_bi_url=project.get("power_bi_url") or "",
        github_url=project.get("github_url") or "",
        etc_url=project.get("report_url") or "",
        thumbnail_url=project.get("thumbnail_url") or "",
        is_public=bool(project.get("is_public")),
        show_visibility_setting=True,
        submit_label="수정 완료",
        secondary_label="목록으로 돌아가기",
    )

    if cancelled:
        st.session_state.pop("editing_project_id", None)
        st.rerun()

    if not submitted:
        return

    parsed_body, missing, url_error = validate_project_form(form_data)
    if missing:
        st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
        return
    if url_error:
        st.error(url_error)
        return

    result = update_project(
        project["id"],
        author_id,
        build_project_payload(form_data, parsed_body),
    )

    if result.ok:
        st.session_state.pop("editing_project_id", None)
        st.session_state["portfolio_notice"] = result.message
        st.rerun()
    else:
        st.error(result.message)
