import streamlit as st

from folio_app.components.auth_validation import is_valid_email, normalize_email
from folio_app.services.auth import (
    complete_password_reset,
    complete_password_reset_with_code,
    complete_password_reset_with_token_hash,
    get_password_reset_tokens,
    request_password_reset,
)


def query_value(name: str) -> str:
    value = st.query_params.get(name, "")
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def render_password_reset_form(default_email: str = "") -> None:
    with st.container(border=False, key="password_reset_panel"):
        st.caption("가입한 이메일을 입력하면 비밀번호 재설정 메일을 보내드립니다.")
        reset_email = normalize_email(
            st.text_input(
                "재설정 메일을 받을 이메일",
                value=default_email if is_valid_email(default_email) else "",
                placeholder="name@example.com",
                key="password_reset_email",
            )
        )
        if reset_email and not is_valid_email(reset_email):
            st.error("이메일 형식을 확인하세요. 예: name@example.com")

        if st.button(
            "재설정 메일 받기",
            key="password_reset_submit",
            use_container_width=True,
        ):
            if not is_valid_email(reset_email):
                st.error("재설정 메일을 받을 이메일을 올바르게 입력하세요.")
                return
            result = request_password_reset(reset_email)
            if result.ok:
                st.success(result.message)
            else:
                st.error(result.message)


def render_password_update_form() -> None:
    saved_access_token, saved_refresh_token = get_password_reset_tokens()
    access_token = saved_access_token or query_value("access_token")
    refresh_token = saved_refresh_token or query_value("refresh_token")
    reset_code = query_value("code")
    recovery_type = query_value("type")
    token_hash = query_value("token_hash") or query_value("token")
    if recovery_type and recovery_type != "recovery":
        token_hash = ""
    if not reset_code and not token_hash and (not access_token or not refresh_token):
        st.error(
            "비밀번호 재설정 인증값이 링크에 없습니다. Supabase Reset Password 이메일 템플릿의 버튼 링크에 "
            "`token_hash={{ .TokenHash }}&type=recovery`가 포함되어 있는지 확인하세요."
        )
        if st.button("로그인으로 돌아가기", key="password_reset_missing_back", use_container_width=True):
            st.query_params.clear()
            st.query_params["page"] = "Login"
            st.rerun()
        return

    st.info("새 비밀번호를 입력하세요. 변경 후 새 비밀번호로 다시 로그인할 수 있습니다.")
    with st.form("password_update_form", clear_on_submit=False):
        new_password = st.text_input("새 비밀번호", type="password", placeholder="8자 이상 입력")
        new_password_confirm = st.text_input("새 비밀번호 확인", type="password")
        submitted = st.form_submit_button("비밀번호 변경", type="primary", use_container_width=True)

    if not submitted:
        return
    if len(new_password) < 8:
        st.error("비밀번호는 최소 8자 이상으로 입력하세요.")
        return
    if new_password != new_password_confirm:
        st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        return

    if saved_access_token and saved_refresh_token:
        result = complete_password_reset(saved_access_token, saved_refresh_token, new_password)
    elif reset_code:
        result = complete_password_reset_with_code(reset_code, new_password)
    elif token_hash:
        result = complete_password_reset_with_token_hash(token_hash, new_password)
    else:
        result = complete_password_reset(access_token, refresh_token, new_password)
    if result.ok:
        st.session_state["login_notice"] = result.message
        st.query_params.clear()
        st.query_params["page"] = "Login"
        st.rerun()
    else:
        st.error(result.message)

