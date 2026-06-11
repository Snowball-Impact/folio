import streamlit as st
from time import time

from folio_app.services.auth import resend_signup_confirmation, sign_in, sign_up
from folio_app.services.profiles import profile_exists_for_email


RESEND_COOLDOWN_SECONDS = 60


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
    except Exception:
        return False


def _render_email_feedback(email: str, already_registered: bool) -> None:
    if not email:
        return

    if not _is_valid_email(email):
        st.error("이메일 형식을 확인하세요. 예: name@example.com")
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


def _is_signup_form_valid(
    email: str,
    password: str,
    password_confirm: str,
    name: str,
    organization: str,
    email_registered: bool,
) -> bool:
    return all(
        [
            _is_valid_email(email),
            not email_registered,
            len(password) >= 8,
            password == password_confirm,
            bool(name),
            bool(organization),
        ]
    )


def _resend_cooldown_remaining() -> int:
    available_at = st.session_state.get("resend_confirmation_available_at", 0)
    return max(0, int(available_at - time()))


def render_login() -> None:
    with st.container(border=True):
        _render_auth_card_header(
            "Login",
            "로그인",
            "등록한 프로젝트와 포트폴리오를 이어서 관리하세요.",
            "login",
        )
        with st.container(border=True):
            st.markdown('<div class="folio-auth-form-card"></div>', unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("이메일", placeholder="name@example.com")
                password = st.text_input("비밀번호", type="password")
                submitted = st.form_submit_button("로그인", use_container_width=True)
            st.markdown(
                '<a class="folio-auth-switch" href="?page=Sign Up" target="_self">처음이라면 회원가입하기</a>',
                unsafe_allow_html=True,
            )

    if submitted:
        email = _normalize_email(email)
        if not email or not password:
            st.error("이메일과 비밀번호를 입력하세요.")
            return

        result = sign_in(email, password)
        if result.ok:
            st.success(result.message)
            st.rerun()
        else:
            st.error(result.message)


def render_signup() -> None:
    with st.container(border=True):
        _render_auth_card_header(
            "Sign Up",
            "회원가입",
            "이메일 인증 후 프로젝트를 등록하고 공유할 수 있습니다.",
            "signup",
        )
        with st.container(border=True):
            st.markdown('<div class="folio-auth-form-card"></div>', unsafe_allow_html=True)
            email = _normalize_email(st.text_input("이메일", placeholder="name@example.com"))
            email_registered = _email_already_registered(email)
            _render_email_feedback(email, email_registered)

            password = st.text_input(
                "비밀번호",
                type="password",
                help="최소 8자 이상을 권장합니다.",
            )
            _render_password_feedback(password)

            password_confirm = st.text_input("비밀번호 확인", type="password")
            _render_password_confirm_feedback(password, password_confirm)

            name = st.text_input("이름", placeholder="홍길동").strip()

            organization = st.text_input("소속", placeholder="학교, 기관, 회사명을 입력하세요").strip()

            submitted = st.button(
                "회원가입",
                disabled=not _is_signup_form_valid(
                    email,
                    password,
                    password_confirm,
                    name,
                    organization,
                    email_registered,
                ),
                use_container_width=True,
            )

            if submitted:
                missing = [
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
                if missing:
                    st.error(f"필수 입력값을 확인하세요: {', '.join(missing)}")
                    return
                if not _is_valid_email(email):
                    st.error("올바른 이메일 주소를 입력하세요.")
                    return
                if _email_already_registered(email):
                    st.error("이미 가입된 이메일입니다. Login 메뉴에서 로그인하세요.")
                    return
                if len(password) < 8:
                    st.error("비밀번호는 최소 8자 이상으로 입력하세요.")
                    return
                if password != password_confirm:
                    st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
                    return

                result = sign_up(email, password, name, organization)
                if result.ok:
                    st.success(result.message)
                    st.caption("인증 메일이 보이지 않으면 스팸함을 확인하거나 잠시 후 다시 시도하세요.")
                else:
                    st.error(result.message)

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
                        st.caption("메일이 보이지 않으면 스팸함을 확인하세요. 재발송은 60초 후 다시 가능합니다.")
                    else:
                        st.error(result.message)


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
