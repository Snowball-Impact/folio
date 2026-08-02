import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.auth_password_reset import (
    query_value,
    render_password_reset_form,
    render_password_update_form,
)
from folio_app.components.auth_validation import normalize_email
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user, sign_in


def render_login() -> None:
    if get_current_user() is not None and query_value("reset") != "1":
        navigate("Home")

    login_notice = st.session_state.pop("login_notice", None)

    with st.container(border=False, key="folio_auth_shell"):
        render_auth_card_header(
            "Login",
            "로그인",
            "등록한 프로젝트와 포트폴리오를 이어서 관리하세요.",
            "login",
        )
        with st.container(border=False, key="folio_auth_form"):
            if login_notice:
                st.info(login_notice)
            if query_value("reset") == "1":
                render_password_update_form()
                return

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("이메일", placeholder="name@example.com")
                password = st.text_input("비밀번호", type="password")
                submitted = st.form_submit_button("로그인", width="stretch")

            login_feedback = st.empty()
            if submitted:
                email = normalize_email(email)
                with login_feedback.container():
                    if not email or not password:
                        st.error("이메일과 비밀번호를 입력하세요.")
                    else:
                        result = sign_in(email, password)
                        if result.ok:
                            track_event("login", {"method": "email"})
                            navigate("Home")
                        else:
                            st.error(result.message)

            render_login_secondary_actions(email)


def render_login_secondary_actions(default_email: str = "") -> None:
    with st.container(border=False, key="login_secondary_actions"):
        reset_col, signup_col = st.columns(2)
        with reset_col:
            if st.button("비밀번호 찾기", key="login_password_reset_toggle", use_container_width=True):
                st.session_state["show_password_reset"] = not st.session_state.get("show_password_reset", False)
        with signup_col:
            if st.button("회원가입하기", key="login_to_signup", use_container_width=True):
                navigate("Sign Up")

    if st.session_state.get("show_password_reset"):
        render_password_reset_form(default_email)


def render_auth_card_header(eyebrow: str, title: str, body: str, variant: str) -> None:
    st.markdown(
        f"""
        <div class="folio-auth-card-header folio-auth-card-{variant}">
            <h2>{title}</h2>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

