import streamlit as st

from folio_app.navigation import navigate
from folio_app.services.auth import get_current_user
from folio_app.services.profiles import OnboardingStatus, complete_onboarding, get_onboarding_status


POLICY_LABELS = {
    "terms": "서비스 이용약관",
    "privacy": "개인정보 처리방침",
}


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

    st.markdown(
        """
        <section class="folio-page-hero folio-onboarding-hero">
            <h1>서비스 이용을 시작하기 전</h1>
            <p class="folio-muted">서비스 이용약관과 개인정보 처리방침을 확인하고 동의해 주세요.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True, key="folio_onboarding_card"):
        with st.form("onboarding_form", clear_on_submit=False):
            st.markdown("### 필수 동의")
            agreed_policy_ids: list[str] = []
            for policy_type in ("terms", "privacy"):
                policy = policies.get(policy_type)
                if not policy:
                    continue

                with st.expander(f"{POLICY_LABELS[policy_type]} 보기", expanded=False):
                    if policy.get("summary"):
                        st.markdown(f"**요약**  \n{policy['summary']}")
                    st.markdown(policy.get("content") or "정책 본문이 아직 등록되지 않았습니다.")
                    if policy.get("content_url"):
                        st.markdown(f"[전문 링크]({policy['content_url']})")

                label = _policy_label(policy_type, policy)
                agreed = st.checkbox(label, key=f"onboarding_agree_{policy_type}")
                if agreed:
                    agreed_policy_ids.append(policy["id"])

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
    except Exception as exc:
        st.error(f"온보딩 정보를 저장하지 못했습니다. ({exc})")
        return

    st.session_state[f"onboarding_done_{user['id']}"] = True
    navigate("Home")


def _policy_label(policy_type: str, policy: dict) -> str:
    label = POLICY_LABELS.get(policy_type, policy_type)
    version = policy.get("version")
    title = policy.get("title") or label
    if version:
        return f"[필수] {title} ({version})에 동의합니다."
    return f"[필수] {title}에 동의합니다."
