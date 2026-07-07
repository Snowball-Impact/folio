import streamlit as st

from folio_app.components.policy_consent import render_policy_agreement_fields
from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.profiles import (
    OnboardingStatus,
    ProfileServiceError,
    complete_onboarding,
    get_onboarding_status,
)


def render(status: OnboardingStatus | None = None) -> None:
    user = get_current_user()
    if user is None:
        navigate("Login")

    status = status or get_onboarding_status(user["id"])
    if status.error_message:
        st.error(status.error_message)
        if st.button("다시 시도", key="retry_onboarding_page"):
            st.rerun()
        return
    if not status.required or status.is_complete:
        navigate("Home")

    policies = status.policies
    is_policy_update = bool(status.consented_policy_ids)

    if is_policy_update:
        badge = "정책 업데이트"
        heading = "이용약관이 새롭게 개정되었어요"
        subtext = "이전에 동의하신 약관 중 일부 내용이 바뀌었습니다. 서비스를 계속 이용하시려면 아래 변경된 내용을 확인하고 다시 동의해 주세요."
    else:
        badge = "서비스 시작"
        heading = "서비스 이용을 시작하기 전"
        subtext = "서비스 이용약관과 개인정보 처리방침을 확인하고 동의해 주세요."

    effective_date = next(
        (str(policy.get("effective_at"))[:10] for policy in policies.values() if policy.get("effective_at")),
        None,
    )
    effective_html = (
        f'<p class="folio-onboarding-effective">{effective_date}부터 적용되는 내용입니다.</p>'
        if is_policy_update and effective_date
        else ""
    )

    st.markdown(
        f"""
        <section class="folio-page-hero folio-onboarding-hero">
            <span class="folio-onboarding-badge">{badge}</span>
            <h1>{heading}</h1>
            <p class="folio-muted">{subtext}</p>
            {effective_html}
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True, key="folio_onboarding_card"):
        with st.form("onboarding_form", clear_on_submit=False):
            st.markdown("### 필수 동의")
            agreed_policy_ids = render_policy_agreement_fields(policies, key_prefix="onboarding")
            submitted = st.form_submit_button("동의하고 시작하기", use_container_width=True)

    if not submitted:
        return

    missing = []
    required_policy_ids = [policy["id"] for policy in policies.values() if policy.get("id")]
    if set(agreed_policy_ids) != set(required_policy_ids):
        missing.append("필수 정책 동의")

    if missing:
        st.error(f"필수 항목을 확인하세요: {', '.join(missing)}")
        return

    try:
        complete_onboarding(user["id"], agreed_policy_ids)
    except ProfileServiceError as exc:
        st.error(str(exc))
        return

    st.session_state[f"onboarding_done_{user['id']}"] = True
    navigate("Home")
