import streamlit as st

from folio_app.components.layout import render_hero, render_placeholder_card
from folio_app.services.auth import get_current_user
from folio_app.services.profiles import get_profile


def render_submit() -> None:
    render_hero(
        "Submit",
        "새 프로젝트 등록",
        "Week 2에서 Supabase projects 테이블과 연결됩니다.",
    )
    st.text_input("프로젝트명", disabled=True)
    st.selectbox("카테고리", ["Data Analytics", "Power BI", "Public Data", "ML"], disabled=True)
    st.text_area("문제 정의", disabled=True)
    st.text_area("핵심 인사이트", disabled=True)
    st.button("프로젝트 등록하기", disabled=True, use_container_width=True)


def render_my_portfolio() -> None:
    render_hero(
        "Portfolio",
        "내 포트폴리오",
        "내가 등록한 데이터 분석 프로젝트를 관리하세요.",
    )
    render_placeholder_card(
        "프로젝트가 아직 없습니다",
        "Week 2 프로젝트 등록 기능이 연결되면 내 프로젝트가 이곳에 표시됩니다.",
    )


def render_profile() -> None:
    user = get_current_user()
    profile = get_profile(user["id"]) if user else None

    render_hero(
        "Profile",
        "프로필",
        "작성자의 기본 정보와 등록 프로젝트를 보여줍니다.",
    )

    if not user:
        st.warning("로그인이 필요합니다.")
        return

    data = profile or {}
    st.markdown(
        f"""
        <div class="folio-card">
            <h3>{data.get("name") or user.get("email")}</h3>
            <p class="folio-muted">이메일: {data.get("email") or user.get("email")}</p>
            <p class="folio-muted">기관: {data.get("organization") or "-"}</p>
            <p class="folio-muted">등록 프로젝트: 0개</p>
            <p class="folio-muted">총 조회수: 0</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
