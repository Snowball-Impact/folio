from __future__ import annotations

import streamlit as st

from folio_app.components.policy_consent import POLICY_LABELS
from folio_app.services.profiles import get_required_policy_versions


def render() -> None:
    policy_type = st.query_params.get("type")
    if policy_type not in {"privacy", "terms"}:
        policy_type = "privacy"

    policies = get_required_policy_versions()
    selected_policy = policies.get(policy_type)
    title = POLICY_LABELS.get(policy_type, "정책 안내")

    st.markdown(
        f"""
        <section class="folio-policy-page">
            <p class="folio-policy-eyebrow">FOLIO POLICY</p>
            <h1>{title}</h1>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if not selected_policy:
        st.info("현재 표시할 정책 본문이 없습니다. 문의가 필요하면 ggmaeng@gmail.com으로 연락해 주세요.")
        return

    meta = []
    if selected_policy.get("version"):
        meta.append(f"버전 {selected_policy['version']}")
    if selected_policy.get("effective_at"):
        meta.append(f"시행일 {str(selected_policy['effective_at'])[:10]}")
    if meta:
        st.caption(" · ".join(meta))

    if selected_policy.get("summary"):
        st.markdown(f"**요약**  \n{selected_policy['summary']}")

    st.markdown(selected_policy.get("content") or "정책 본문이 아직 등록되지 않았습니다.")

    if selected_policy.get("content_url"):
        st.markdown(f"[전문 링크]({selected_policy['content_url']})")
