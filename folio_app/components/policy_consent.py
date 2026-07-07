import streamlit as st


POLICY_LABELS = {
    "terms": "서비스 이용약관",
    "privacy": "개인정보 처리방침",
}


def render_policy_agreement_fields(policies: dict[str, dict], key_prefix: str) -> list[str]:
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
        agreed = st.checkbox(label, key=f"{key_prefix}_agree_{policy_type}")
        if agreed:
            agreed_policy_ids.append(policy["id"])
    return agreed_policy_ids


def _policy_label(policy_type: str, policy: dict) -> str:
    label = POLICY_LABELS.get(policy_type, policy_type)
    version = policy.get("version")
    title = policy.get("title") or label
    if version:
        return f"[필수] {title} ({version})에 동의합니다."
    return f"[필수] {title}에 동의합니다."
