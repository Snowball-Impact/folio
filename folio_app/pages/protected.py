import streamlit as st

from folio_app.components.layout import render_hero
from folio_app.components.portfolio_items import render_portfolio_item
from folio_app.components.project_editor import render_edit_project_form, render_submit_project_form
from folio_app.components.profile_summary import profile_overview_html
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.comments import annotate_unread_comment_status
from folio_app.services.profiles import ProfileServiceError, get_profile, update_profile
from folio_app.services.projects import (
    ProjectServiceError,
    clear_project_caches,
    count_author_stats,
    delete_project,
    list_projects_by_author,
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

    if not user:
        render_hero(
            "Submit",
            "새 프로젝트 등록",
            "당신의 데이터 분석 프로젝트를 포트폴리오로 공개하세요.",
            image_name="hero-submit.png",
            image_alt="데이터 분석 프로젝트 등록 화면 일러스트",
        )
        _render_login_required("submit", "프로젝트를 등록하려면 로그인이 필요합니다.")
        return

    render_submit_project_form(user["id"])


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
        annotate_unread_comment_status(projects, user["id"])
    except ProjectServiceError as exc:
        st.error(str(exc))
        if st.button("다시 시도", key="retry_my_portfolio"):
            clear_project_caches()
            st.rerun()
        return
    unread_comment_error = st.session_state.pop("portfolio_unread_comment_error", None)
    if unread_comment_error:
        st.warning(unread_comment_error)

    if editing_project_id:
        project = next((item for item in projects if item["id"] == editing_project_id), None)
        if project:
            render_edit_project_form(user["id"], project)
            return
        st.session_state.pop("editing_project_id", None)
        st.rerun()

    try:
        profile = get_profile(user["id"])
    except ProfileServiceError as exc:
        st.error(str(exc))
        if st.button("프로필 다시 불러오기", key="retry_my_profile"):
            st.rerun()
        return
    if profile is None:
        st.info("프로필 정보가 아직 생성되지 않았습니다. 다시 로그인한 뒤 시도하세요.")
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

    with st.container(border=True, key="profile_overview"):
        st.markdown(profile_overview_html(user, profile, projects, stats), unsafe_allow_html=True)

        if st.button("프로필 편집", key="start_edit_profile", icon=":material/edit:"):
            st.session_state["editing_profile"] = True
            st.rerun()

    st.markdown(
        """
        <div class="folio-profile-section-heading">
            <h2>내 프로젝트</h2>
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
                    render_portfolio_item(project)
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
                <h3>아직 등록한 프로젝트가 없습니다.</h3>
                <p>첫 프로젝트를 등록하면 이곳에서 관리할 수 있습니다.</p>
                """,
                unsafe_allow_html=True,
            )
            if st.button("프로젝트 등록", key="profile_create_project", type="primary"):
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
    except ProfileServiceError as exc:
        st.error(str(exc))
        return

    st.session_state.pop("editing_profile", None)
    st.success("프로필이 업데이트됐습니다.")
    st.rerun()

