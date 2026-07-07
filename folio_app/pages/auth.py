import streamlit as st
from time import time

from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user, resend_signup_confirmation, sign_in, sign_up
from folio_app.services.profiles import profile_exists_for_email


RESEND_COOLDOWN_SECONDS = 60
EXISTING_ACCOUNT_MESSAGE_PREFIX = "이미 가입된 이메일"


class SignupEmailCheckError(RuntimeError):
    pass


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _is_valid_email(email: str) -> bool:
    if not email or "@" not in email:
        return False

    local, _, domain = email.partition("@")
    return bool(local and "." in domain and not domain.startswith(".") and not domain.endswith("."))


@st.cache_data(ttl=10, show_spinner=False)
def _cached_profile_exists_for_email(email: str) -> bool:
    return profile_exists_for_email(email)


def _email_already_registered(email: str) -> bool:
    if not _is_valid_email(email):
        return False

    try:
        return _cached_profile_exists_for_email(email)
    except Exception as exc:
        raise SignupEmailCheckError("가입 여부를 확인하지 못했습니다. 잠시 후 다시 시도하세요.") from exc


def _render_email_feedback(email: str, already_registered: bool, check_error: str | None = None) -> None:
    if not email:
        return

    if not _is_valid_email(email):
        st.error("이메일 형식을 확인하세요. 예: name@example.com")
    elif check_error:
        st.error(check_error)
    elif already_registered:
        st.warning("이미 가입된 이메일입니다. 인증 전이라면 아래에서 인증 메일을 다시 받으세요.")


def _render_password_feedback(password: str) -> None:
    if not password:
        return

    if len(password) < 8:
        st.warning(f"비밀번호가 너무 짧습니다. 현재 {len(password)}자 / 최소 8자")


def _render_password_confirm_feedback(password: str, password_confirm: str) -> None:
    if not password_confirm:
        return

    if password != password_confirm:
        st.error("비밀번호 확인이 일치하지 않습니다.")


def _signup_missing_required_fields(
    email: str,
    password: str,
    password_confirm: str,
    name: str,
    organization: str,
) -> list[str]:
    return [
        label
        for label, value in {
            "이메일": email,
            "비밀번호": password,
            "비밀번호 확인": password_confirm,
            "이름": name,
            "소속": organization,
        }.items()
        if not value
    ]


def _should_show_resend_confirmation(email_registered: bool) -> bool:
    return email_registered or bool(st.session_state.get("signup_confirmation_email"))


def _is_existing_account_message(message: str) -> bool:
    return message.startswith(EXISTING_ACCOUNT_MESSAGE_PREFIX)


def _should_show_signup_login_link(email_registered: bool, email: str) -> bool:
    return email_registered or st.session_state.get("signup_existing_email") == email


def _render_signup_login_link() -> None:
    if st.button("이미 계정이 있다면 로그인하기", key="signup_to_login", width="stretch"):
        navigate("Login")


def _resend_cooldown_remaining() -> int:
    available_at = st.session_state.get("resend_confirmation_available_at", 0)
    return max(0, int(available_at - time()))


def render_login() -> None:
    if get_current_user() is not None:
        navigate("Home")

    login_notice = st.session_state.pop("login_notice", None)

    with st.container(border=False, key="folio_auth_shell"):
        _render_auth_card_header(
            "Login",
            "로그인",
            "등록한 프로젝트와 포트폴리오를 이어서 관리하세요.",
            "login",
        )
        with st.container(border=False, key="folio_auth_form"):
            if login_notice:
                st.info(login_notice)

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("이메일", placeholder="name@example.com")
                password = st.text_input("비밀번호", type="password")
                submitted = st.form_submit_button("로그인", width="stretch")

            login_feedback = st.empty()
            if submitted:
                email = _normalize_email(email)
                with login_feedback.container():
                    if not email or not password:
                        st.error("이메일과 비밀번호를 입력하세요.")
                    else:
                        result = sign_in(email, password)
                        if result.ok:
                            navigate("Home")
                        else:
                            st.error(result.message)

            if st.button("처음이라면 회원가입하기", key="login_to_signup", width="stretch"):
                navigate("Sign Up")


def render_signup() -> None:
    with st.container(border=False, key="folio_auth_shell"):
        _render_auth_card_header(
            "Sign Up",
            "회원가입",
            "이메일 인증 후 프로젝트를 등록하고 공유할 수 있습니다.",
            "signup",
        )
        with st.container(border=False, key="folio_auth_form"):
            email = _normalize_email(st.text_input("이메일 *", placeholder="name@example.com"))
            email_registered = False
            email_check_error = None
            try:
                email_registered = _email_already_registered(email)
            except SignupEmailCheckError as exc:
                email_check_error = str(exc)
            _render_email_feedback(email, email_registered, email_check_error)

            password = st.text_input(
                "비밀번호 *",
                type="password",
                placeholder="8자 이상 입력",
            )
            _render_password_feedback(password)

            password_confirm = st.text_input("비밀번호 확인 *", type="password")
            _render_password_confirm_feedback(password, password_confirm)

            name = st.text_input("이름 *", placeholder="홍길동").strip()

            organization = st.text_input(
                "소속 *",
                placeholder="개인, 학원, 교육과정, 학교, 기관, 회사명을 입력하세요",
            ).strip()

            submitted = st.button(
                "회원가입",
                use_container_width=True,
            )

            if submitted:
                missing = _signup_missing_required_fields(email, password, password_confirm, name, organization)
                if missing:
                    st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
                    return
                if not _is_valid_email(email):
                    st.error("올바른 이메일 주소를 입력하세요.")
                    return
                try:
                    email_registered = _email_already_registered(email)
                except SignupEmailCheckError as exc:
                    st.error(str(exc))
                    return
                if email_registered:
                    st.session_state["signup_existing_email"] = email
                    st.error("이미 가입된 이메일입니다. Login 메뉴에서 로그인하세요.")
                    _render_signup_login_link()
                    return
                if len(password) < 8:
                    st.error("비밀번호는 최소 8자 이상으로 입력하세요.")
                    return
                if password != password_confirm:
                    st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
                    return

                result = sign_up(email, password, name, organization)
                if result.ok:
                    st.session_state["signup_confirmation_email"] = email
                    st.session_state["resend_confirmation_email"] = email
                    st.session_state.pop("signup_existing_email", None)
                    st.success(result.message)
                    st.caption("메일이 보이지 않으면 스팸함을 확인하세요. 이미 가입한 이메일이라면 로그인하거나 인증 메일 다시 받기를 이용하세요.")
                else:
                    if _is_existing_account_message(result.message):
                        st.session_state["signup_existing_email"] = email
                    st.error(result.message)

            if _should_show_resend_confirmation(email_registered):
                with st.expander("인증 메일 다시 받기", expanded=False):
                    st.caption("인증 메일을 받지 못했거나 링크가 만료됐다면 다시 요청하세요.")

                    if email_registered and st.session_state.get("resend_confirmation_email", "") != email:
                        st.session_state["resend_confirmation_email"] = email

                    resend_email = _normalize_email(
                        st.text_input(
                            "인증 메일 재발송 이메일",
                            placeholder="name@example.com",
                            key="resend_confirmation_email",
                        )
                    )
                    if resend_email and not _is_valid_email(resend_email):
                        st.error("재발송할 이메일 형식을 확인하세요.")

                    cooldown_remaining = _resend_cooldown_remaining()
                    if cooldown_remaining:
                        st.caption(f"인증 메일은 {cooldown_remaining}초 후 다시 요청할 수 있습니다.")

                    resend_submitted = st.button(
                        "인증 메일 다시 보내기",
                        disabled=not _is_valid_email(resend_email) or cooldown_remaining > 0,
                        use_container_width=True,
                    )

                    if resend_submitted:
                        result = resend_signup_confirmation(resend_email)
                        if result.ok:
                            st.session_state["resend_confirmation_available_at"] = time() + RESEND_COOLDOWN_SECONDS
                            st.success(result.message)
                            st.caption("메일이 보이지 않으면 스팸함을 확인하세요. 재요청은 60초 후 다시 가능합니다.")
                        else:
                            st.error(result.message)

            if _should_show_signup_login_link(email_registered, email):
                _render_signup_login_link()


def _render_auth_card_header(eyebrow: str, title: str, body: str, variant: str) -> None:
    st.markdown(
        f"""
        <div class="folio-auth-card-header folio-auth-card-{variant}">
            <h2>{title}</h2>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
