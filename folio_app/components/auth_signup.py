from time import time

import streamlit as st

from folio_app.components.analytics import track_event
from folio_app.components.auth_login import render_auth_card_header
from folio_app.components.auth_validation import (
    SignupEmailCheckError,
    email_already_registered,
    is_existing_account_message,
    is_valid_email,
    normalize_email,
    signup_missing_required_fields,
    signup_required_policies,
)
from folio_app.components.policy_consent import render_policy_agreement_fields
from folio_app.navigation import navigate
from folio_app.services.auth import resend_signup_confirmation, sign_up


RESEND_COOLDOWN_SECONDS = 60


def should_show_resend_confirmation(email_registered: bool) -> bool:
    return email_registered or bool(st.session_state.get("signup_confirmation_email"))


def should_show_signup_login_link(email_registered: bool, email: str) -> bool:
    return email_registered or st.session_state.get("signup_existing_email") == email


def render_signup() -> None:
    with st.container(border=False, key="folio_auth_shell"):
        render_auth_card_header(
            "Sign Up",
            "회원가입",
            "이메일 인증 후 프로젝트를 등록하고 공유할 수 있습니다.",
            "signup",
        )
        with st.container(border=False, key="folio_auth_form"):
            email = normalize_email(st.text_input("이메일 *", placeholder="name@example.com"))
            email_registered = False
            email_check_error = None
            try:
                email_registered = email_already_registered(email)
            except SignupEmailCheckError as exc:
                email_check_error = str(exc)
            render_email_feedback(email, email_registered, email_check_error)

            password = st.text_input(
                "비밀번호 *",
                type="password",
                placeholder="8자 이상 입력",
            )
            render_password_feedback(password)

            password_confirm = st.text_input("비밀번호 확인 *", type="password")
            render_password_confirm_feedback(password, password_confirm)

            name = st.text_input("이름 *", placeholder="홍길동").strip()

            organization = st.text_input(
                "소속 *",
                placeholder="개인, 학원, 교육과정, 학교, 기관, 회사명을 입력하세요",
            ).strip()

            required_policies = signup_required_policies()
            agreed_policy_ids: list[str] = []
            if required_policies:
                st.markdown("#### 필수 동의")
                agreed_policy_ids = render_policy_agreement_fields(required_policies, key_prefix="signup")

            submitted = st.button(
                "회원가입",
                use_container_width=True,
            )

            if submitted:
                if not validate_and_submit_signup(
                    email,
                    password,
                    password_confirm,
                    name,
                    organization,
                    required_policies,
                    agreed_policy_ids,
                ):
                    return

            if should_show_resend_confirmation(email_registered):
                render_resend_confirmation(email_registered, email)

            if should_show_signup_login_link(email_registered, email):
                render_signup_login_link()


def validate_and_submit_signup(
    email: str,
    password: str,
    password_confirm: str,
    name: str,
    organization: str,
    required_policies: dict,
    agreed_policy_ids: list[str],
) -> bool:
    missing = signup_missing_required_fields(email, password, password_confirm, name, organization)
    if missing:
        st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
        return False
    if not is_valid_email(email):
        st.error("올바른 이메일 주소를 입력하세요.")
        return False
    required_policy_ids = [policy["id"] for policy in required_policies.values() if policy.get("id")]
    if set(agreed_policy_ids) != set(required_policy_ids):
        st.error("필수 약관과 개인정보 처리방침에 모두 동의해야 가입할 수 있습니다.")
        return False
    try:
        email_registered = email_already_registered(email)
    except SignupEmailCheckError as exc:
        st.error(str(exc))
        return False
    if email_registered:
        st.session_state["signup_existing_email"] = email
        st.error("이미 가입된 이메일입니다. Login 메뉴에서 로그인하세요.")
        render_signup_login_link()
        return False
    if len(password) < 8:
        st.error("비밀번호는 최소 8자 이상으로 입력하세요.")
        return False
    if password != password_confirm:
        st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        return False

    result = sign_up(email, password, name, organization, agreed_policy_ids)
    if result.ok:
        track_event("sign_up", {"method": "email"})
        st.session_state["signup_confirmation_email"] = email
        st.session_state["resend_confirmation_email"] = email
        st.session_state.pop("signup_existing_email", None)
        st.success(result.message)
        st.caption("메일이 보이지 않으면 스팸함을 확인하세요. 이미 가입한 이메일이라면 로그인하거나 인증 메일 다시 받기를 이용하세요.")
        return True

    if is_existing_account_message(result.message):
        st.session_state["signup_existing_email"] = email
    st.error(result.message)
    return False


def render_email_feedback(email: str, already_registered: bool, check_error: str | None = None) -> None:
    if not email:
        return

    if not is_valid_email(email):
        st.error("이메일 형식을 확인하세요. 예: name@example.com")
    elif check_error:
        st.error(check_error)
    elif already_registered:
        st.warning("이미 가입된 이메일입니다. 인증 전이라면 아래에서 인증 메일을 다시 받으세요.")


def render_password_feedback(password: str) -> None:
    if not password:
        return

    if len(password) < 8:
        st.warning(f"비밀번호가 너무 짧습니다. 현재 {len(password)}자 / 최소 8자")


def render_password_confirm_feedback(password: str, password_confirm: str) -> None:
    if not password_confirm:
        return

    if password != password_confirm:
        st.error("비밀번호 확인이 일치하지 않습니다.")


def render_signup_login_link() -> None:
    if st.button("이미 계정이 있다면 로그인하기", key="signup_to_login", width="stretch"):
        navigate("Login")


def resend_cooldown_remaining() -> int:
    available_at = st.session_state.get("resend_confirmation_available_at", 0)
    return max(0, int(available_at - time()))


def render_resend_confirmation(email_registered: bool, email: str) -> None:
    with st.expander("인증 메일 다시 받기", expanded=False):
        st.caption("인증 메일을 받지 못했거나 링크가 만료됐다면 다시 요청하세요.")

        if email_registered and st.session_state.get("resend_confirmation_email", "") != email:
            st.session_state["resend_confirmation_email"] = email

        resend_email = normalize_email(
            st.text_input(
                "인증 메일 재발송 이메일",
                placeholder="name@example.com",
                key="resend_confirmation_email",
            )
        )
        if resend_email and not is_valid_email(resend_email):
            st.error("재발송할 이메일 형식을 확인하세요.")

        cooldown_remaining = resend_cooldown_remaining()
        if cooldown_remaining:
            st.caption(f"인증 메일은 {cooldown_remaining}초 후 다시 요청할 수 있습니다.")

        resend_submitted = st.button(
            "인증 메일 다시 보내기",
            disabled=cooldown_remaining > 0,
            use_container_width=True,
        )

        if resend_submitted:
            if not is_valid_email(resend_email):
                st.error("재발송할 이메일을 올바르게 입력하세요.")
                return
            result = resend_signup_confirmation(resend_email)
            if result.ok:
                st.session_state["resend_confirmation_available_at"] = time() + RESEND_COOLDOWN_SECONDS
                st.success(result.message)
                st.caption("메일이 보이지 않으면 스팸함을 확인하세요. 재요청은 60초 후 다시 가능합니다.")
            else:
                st.error(result.message)

